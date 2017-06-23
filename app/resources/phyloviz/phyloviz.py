from app import app, db
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with #filters data according to some fields
from flask_security import current_user
from flask import jsonify

from flask_security import current_user, login_required, roles_required, auth_token_required
import datetime

from config import CURRENT_ROOT, JOBS_ROOT

from app.models.models import Protocol
from app.models.models import Strain
from app.models.models import Report
import json
import requests
import subprocess
import random
import string

phyloviz_post_parser = reqparse.RequestParser()
'''phyloviz_post_parser.add_argument('headers_profile', dest='headers_profile', type=str, required=True, help="profile headers")
phyloviz_post_parser.add_argument('body_profile', dest='body_profile', type=str, required=True, help="profile body")
phyloviz_post_parser.add_argument('headers_metadata', dest='headers_metadata', type=str, required=True, help="metadata headers")
phyloviz_post_parser.add_argument('body_metadata', dest='body_metadata', type=str, required=True, help="metadata body")
phyloviz_post_parser.add_argument('dataset_name', dest='dataset_name', type=str, required=True, help="dataset name")
phyloviz_post_parser.add_argument('dataset_description', dest='dataset_description', type=str, required=True, help="dataset description")'''

phyloviz_post_parser.add_argument('job_ids', dest='job_ids', type=str, required=True, help="Job ids")
phyloviz_post_parser.add_argument('dataset_name', dest='dataset_name', type=str, required=True, help="dataset name")
phyloviz_post_parser.add_argument('dataset_description', dest='dataset_description', type=str, required=True, help="dataset description")
phyloviz_post_parser.add_argument('additional_data', dest='additional_data', type=str, required=True, help="additional metadata")
#Load job results to display on graphical interface
class PHYLOViZResource(Resource):

	@login_required
	def post(self):
		args = phyloviz_post_parser.parse_args()

		file_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))

		file_path_profile = './app/uploads/'+file_name+'_profile.tab'

		file_path_metadata = './app/uploads/'+file_name+'_metadata.tab'

		to_replace = {"LNF": "0", "INF-": "", "NIPHEM": "0", "NIPH": "0", "LOTSC": "0", "PLOT3": "0", "PLOT5": "0", "ALM": "0", "ASM": "0"}

		
		headers_profile = ["ID"]
		headers_metadata = ["ID"]
		body_profile = []
		all_profiles = []
		all_metadata = []


		total_j_ids = args.job_ids.split(",")

		first_time = True
		first_time_m = True

		print json.loads(args.additional_data)

		for job_id in total_j_ids:
			body_profile = [];
			report = db.session.query(Report).filter(Report.job_id == job_id).first()
			if not report:
				continue
			else:
				#print report.report_data["run_output"]
				#print report.sample_name

				if first_time == True:
					headers = headers_profile + report.report_data["run_output"]["header"]
					first_time = False

				new_profile = []
				string_list = "\t".join(report.report_data["run_output"]["run_output.fasta"])

				for k,v in to_replace.iteritems():
					string_list = string_list.replace(k,v)
				#new_profile.append(report.sample_name + "\t" + new_allele)

				#print profiles
				all_profiles.append(report.sample_name + "\t" + string_list)

				strain = db.session.query(Strain).filter(Strain.name == report.sample_name).first()

				strain_metadata = json.loads(strain.strain_metadata)

				if first_time_m == True:
					for x in strain_metadata:
						if x == "fileselector":
							continue
						else:
							headers_metadata.append(x)

				first_time_m = False
				
				straind = [report.sample_name]
				for x in strain_metadata:
					if x == "fileselector":
						continue
					else:
						straind.append(strain_metadata[x])

				all_metadata.append('\t'.join(straind) + "\n")


		#WRITE PROFILE FILE
		with open(file_path_profile, 'w') as p_file:
			hd = [];
			
			p_file.write('\t'.join(headers) + '\n')
			
			for y in all_profiles:
				p_file.write(y + '\n')

		#WRITE METADATA FILE
		with open(file_path_metadata, "w") as p_file:			
			p_file.write("\t".join(headers_metadata) + "\n")
			
			for y in all_metadata:
				p_file.write(y + "\n")

		command = 'python ./app/resources/phyloviz/remoteUpload.py -u innuendo_demo -p innuendo_demo -sdt profile -sd ' + file_path_profile + ' -m '+ file_path_metadata +' -d ' + args.dataset_name + ' -dn ' + args.dataset_description + '-l';
		#command = 'python ./app/resources/phyloviz/remoteUpload.py -u innuendo_demo -p innuendo_demo -sdt profile -sd ' + file_path_profile + ' -d ' + args.dataset_name + ' -dn ' + args.dataset_description + '-l';
		command = command.split(' ')
		print command
		proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout, stderr = proc.communicate()

		print stdout, stderr

		return stdout, 200
		


