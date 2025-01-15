from flask import jsonify, request
from app.models.command import Command
from app.db import db
from app.models.system import System
import time
import subprocess

class CommandController:
    def create(self):
        currentUser = request.currentUser
        data = request.get_json()
        system = System.query.filter_by(id=data['systemId']).first()
        if not system:
            return jsonify({
            "status": "error", 
            "message": "System not found"
            }), 404
            
        newCommand = Command(
            name=data['name'],
            command=data['command'],
            status=data.get('status', True),
            systemId=data['systemId'],
            durationOfRunning=data.get('durationOfRunning', 0),
            createdBy=currentUser['id'],
            updatedBy=currentUser['id']
        )
        
        db.session.add(newCommand)
        db.session.commit()
        
        return jsonify({'message': 'Command created successfully', 'data': newCommand.toDict()}), 201

    def getAll(self):
        limit = int(request.args.get('limit', 10))
        page = int(request.args.get('page', 1))
        skip = (int(page) - 1) * int(limit)

        search = request.args.get('search', '')
        status = request.args.get('status', '')
        systemId = request.args.get('systemId', '')

        query = db.session.query(Command)
        if search:
            query = query.filter(Command.name.ilike(f'%{search}%'))
        if status:
            statusBool = status.lower() == 'true'
            query = query.filter(Command.status == statusBool)
        if systemId:
            query = query.filter(Command.systemId == int(systemId))
        
        commands = query.order_by(Command.updatedAt.desc()).limit(limit).offset(skip).all()
        total = query.count()
        return jsonify({
            'commands': [command.toDict() for command in commands],
            'meta': {
                'total': total,
                'totalPages': -(-total // int(limit)),
                'currentPage': page,
                'pageSize': limit
            }
        }), 200

    def getOne(self, commandId: int):
        command = Command.query.filter_by(id=commandId).first()
        if not command:
            return jsonify({
                "status": "error",
                "message": "Command not found"
            }), 404
        
        return jsonify({
            "status": "success",
            "data": command.toDict()
        }), 200

    def update(self, commandId: int):
        currentUser = request.currentUser
        command = Command.query.filter_by(id=commandId).first()
        if not command:
            return jsonify({
                "status": "error",
                "message": "Command not found"
            }), 404
        
        system = System.query.filter_by(id=request.json['systemId']).first()
        if not system:
            return jsonify({
                "status": "error",
                "message": "System not found"
            }), 404
        
        data = request.get_json()
        command.name = data.get('name', command.name)
        command.command = data.get('command', command.command)
        command.status = data.get('status', command.status)
        command.systemId = data.get('systemId', command.systemId)
        command.durationOfRunning = data.get('durationOfRunning', command.durationOfRunning)
        command.updatedBy = currentUser['id']

        db.session.commit()
        return jsonify({'message': 'Command updated successfully', 'data': command.toDict()}), 200

    def delete(self, commandId: int):
        command = Command.query.filter_by(id=commandId).first()
        if not command:
            return jsonify({
                "status": "error",
                "message": "Command not found"
            }), 404
        
        db.session.delete(command)
        db.session.commit()
        return jsonify({'message': 'Command deleted successfully'}), 200

    def run(self, commandId: int):
        command = Command.query.filter_by(id=commandId).first()
        if not command:
            return jsonify({
                "status": "error",
                "message": "Command not found"
            }), 404

        try:
            # Execute the command
            result = subprocess.run(command.command, shell=True, capture_output=True, text=True, timeout=command.durationOfRunning)
            output = result.stdout
            error = result.stderr
            return_code = result.returncode

            if return_code != 0:
                return jsonify({
                    "status": "error",
                    "message": f"Command execution failed with error: {error}"
                }), 500

            return jsonify({
                "status": "success",
                "message": f"Command '{command.command}' executed successfully",
                "output": output
            }), 200

        except subprocess.TimeoutExpired:
            return jsonify({
            "status": "success",
            "message": f"Command '{command.command}' timeout after {command.durationOfRunning} seconds as expected"
            }), 200
