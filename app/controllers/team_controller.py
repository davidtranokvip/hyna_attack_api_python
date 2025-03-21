from app.services.response import Response
from app.models.team import Team
from flask import request
from app.db import db

class TeamController:
    def create(self):
        try:
            team = request.get_json()

            if not team.get('name'):
                return Response.error({
                    'name': 'Name is required'
                }, code=400)
            
            is_existed = Team.query.filter(Team.name == team.get('name')).first()
            if is_existed:
                return Response.error({
                   'name': 'Name already registered'
                }, code=400)
            
            newTeam = Team(
                name=team.get('name'),
                parent_id=team.get('parent_id'),
                servers=team.get('servers'),
            )
            db.session.add(newTeam)
            db.session.commit()
            return Response.success(data=[], message="Created Team Success")
            
        except Exception as e:
            db.session.rollback()
            return Response.error(str(e), code=400)
        
    def getAll(self):
        try:

            query = db.session.query(Team)
            teams = query.order_by(Team.updatedAt.desc()).all()
            
            result = [team.toDict() for team in teams]
        
            return Response.success(data=result, message="Get Teams Success")

        except Exception as e:
            db.session.rollback()
            return Response.error(str(e), code=400)

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
            
            return Response.success(data=tree, message="Get Parent Success")
            
        except Exception as e:
            db.session.rollback()
            return Response.error(str(e), code=400)
        
    def update(self, teamId: int): 
        try: 
            team = Team.query.filter_by(id=teamId).first()
            if not team:
                return Response.error("Team not found", code=404)
            
            data = request.get_json()
            is_existed = Team.query.filter(
                Team.name == data.get('name'),
                Team.id != teamId
            ).first()
        
            if is_existed:
                return Response.error({
                        'name': 'Team already registered'
                }, code=400)
            
            if not data.get('name'):
                return Response.error({
                        'name': 'Name is required',
                }, code=400)
            
            data = request.get_json()
            team.name = data.get('name', team.name)
            team.parent_id = data.get('parent_id', team.parent_id)
            team.servers = data.get('servers', team.servers)

            db.session.commit()
            return Response.success(data=[], message="Updated Team Success")
        
        except Exception as e:
            db.session.rollback()
            return Response.error(str(e), code=400) 

    def delete(self, teamId: int):
        try:
            team = Team.query.filter_by(id=teamId).first()
            if not team:
                return Response.error("Team not found", code=404)
            
            db.session.delete(team)
            db.session.commit()
            return Response.success(data=[], message="Team Deleted Success")
        
        except Exception as e:
            db.session.rollback()
            return Response.error(str(e), code=400)