from flask import jsonify, request
from app.models.team import Team
from app.db import db
from app.models.server import Server

class TeamController:
    def create(self):
        try:
            team = request.get_json()

            if not team.get('name'):
                return jsonify({
                    'message': 'name is required',
                    'status': 'error'
                }), 400
            
            newTeam = Team(
                name=team.get('name'),
                parent_id=team.get('parent_id'),
                servers=team.get('servers'),
            )
            db.session.add(newTeam)
            db.session.commit()
            
            return jsonify({
                'message': 'teams created successfully', 
                'status': 'success'
            }), 202
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": "error",
                "message": str(e)   
            }), 400
        
    def getAll(self):
        try:

            query = db.session.query(Team)
            teams = query.order_by(Team.updatedAt.desc()).all()
            
            return jsonify({
                'teams': [team.toDict() for team in teams],
                'status': 'success'
            }), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 400

    def buildTeamTree(self, teams, parent_id=None):
        tree = []
        for team in teams:
            if team.parent_id == parent_id:
                children = self.buildTeamTree(teams, team.id)
                team_dict = team.toDict()
                if children:
                    team_dict['children'] = children
                tree.append(team_dict)
        return tree

    def getParentAll(self):
        try:
            teams = Team.query.order_by(Team.updatedAt.desc()).all()
            
            tree = self.buildTeamTree(teams, parent_id=None)
            
            return jsonify({
                'status': 'success',
                'data': tree
            }), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 400
        
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 400
        
    def update(self, teamId: int): 
        try: 
            team = Team.query.filter_by(id=teamId).first()
            if not team:
                return jsonify({
                    "status": "error",
                    "message": "team not found"
                }), 404
            
            data = request.get_json()
            team.name = data.get('name', team.name)
            team.parent_id = data.get('parent_id', team.parent_id)
            team.servers = data.get('servers', team.servers)

            db.session.commit()
            return jsonify({'message': 'Team updated successfully', 'data': team.toDict(), 'status': 'success'}), 200
        
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 400 


    def delete(self, teamId: int):
        try:
            team = Team.query.filter_by(id=teamId).first()
            if not team:
                return jsonify({
                    "status": "error",
                    "message": "team not found"
                }), 404
            
            db.session.delete(team)
            db.session.commit()
            return jsonify({'message': 'team deleted successfully', 'status': 'success'}), 200
        
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 400