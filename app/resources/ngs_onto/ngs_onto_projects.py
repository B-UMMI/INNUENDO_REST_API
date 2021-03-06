from app import dbconAg
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from app.utils.queryParse2Json import parseAgraphStatementsRes
from flask_security import current_user, login_required, roles_required
from config import obo,localNSpace, processTypes,processMessages
from franz.openrdf.vocabulary.rdf import RDF


# Defining post arguments parser
project_post_parser = reqparse.RequestParser()
project_post_parser.add_argument('study_id', dest='study_id', type=str,
                                 required=True, help="The project id")


class NGSOnto_ProjectListResource(Resource):
    """
    Class for project list operations
    """

    @login_required
    def get(self):
        """Get projects

        This method allows getting all the available projects.

        Returns
        -------
        list: list of projects
        """

        # Agraph
        studyType = dbconAg.createURI(namespace=obo, localname="OBI_0000066")
        statements = dbconAg.getStatements(None, RDF.TYPE, studyType)
        jsonResult=parseAgraphStatementsRes(statements)
        statements.close()

        return jsonResult, 200


class NGSOnto_ProjectUserResource(Resource):
    """
    Class to get specific projects
    """

    @login_required
    def get(self, id):
        """Get specific project

        This method allows getting a specific projct from the NGSOnto database

        Parameters
        ----------
        id: str
            project identifier

        Returns
        -------
        list: list with the query result
        """

        # Agraph
        studyURI = dbconAg.createURI(namespace=localNSpace+"projects/",
                                     localname=str(id))
        statements = dbconAg.getStatements(studyURI, None, None)
        studyAg=parseAgraphStatementsRes(statements)
        statements.close()

        return studyAg, 200


class NGSOnto_ProjectListUserResource(Resource):
    """
    Class to get projects from a specific user
    """

    @login_required
    def get(self):
        """Projects from user

        This method allows getting all the available projects of a given user.
        It requires login.

        Returns
        -------
        list: list of the available projects from that user.
        """

        id = current_user.id
        UserURI = dbconAg.createURI(namespace=localNSpace,
                                    localname="users/"+str(id))
        studyBelong=dbconAg.createURI(namespace=obo, localname="NGS_0000015")
        statements = dbconAg.getStatements(None, studyBelong, UserURI)
        studiesAg=parseAgraphStatementsRes(statements)
        statements.close()

        return studiesAg, 200

    @login_required
    def post(self):
        """Add project

        This method allows adding a project connected to a user in the
        NGSOnto database.
        Requires the project identifier.

        Returns
        -------
        code: 201 if added.
        """

        id = current_user.id
        args = project_post_parser.parse_args()

        newstudyid = args.study_id

        UserURI = dbconAg.createURI(namespace=localNSpace,
                                    localname="users/"+str(id))
        studyBelong2=dbconAg.createURI(namespace=obo, localname="NGS_0000015")
        studyURI = dbconAg.createURI(namespace=localNSpace+"projects/",
                                     localname=str(newstudyid))

        studyType = dbconAg.createURI(namespace=obo, localname="OBI_0000066")

        dbconAg.add(studyURI, RDF.TYPE, studyType)
        dbconAg.add(studyURI, studyBelong2, UserURI)

        return 201
