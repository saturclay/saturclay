import requests # https://stackoverflow.com/questions/2018026/what-are-the-differences-between-the-urllib-urllib2-urllib3-and-requests-modul
import sys
import pickle

URL_SERVER = 'https://beta.vocadb.net'
ALBUM_ID = 27837 # album to add to
TAG_ID = 9403 # tag to add

session = requests.Session()
session.headers.update({
	'user-agent': 'https://github.com/VocaDB/mod-scripts',
})

# ----

def login() -> bool:
	'''Log in to *DB.'''

	'''netrc_auth = netrc.netrc().authenticators(URL_SERVER)
	if not netrc_auth:
		raise LookupError(f'Could not find the {URL_SERVER} machine in .netrc')'''

	print(f'Logging in to {URL_SERVER}')
	_ = session.get(
		f'{URL_SERVER}/api/antiforgery/token'
	)
	request = session.post(
		f'{URL_SERVER}/api/users/login',
		json = {
			'userName': "EventAdder",
			'password': "eventfulmikumiku",
		},
		headers = {
			'requestVerificationToken': session.cookies.get_dict()['XSRF-TOKEN'],
		}
	)

	if request.status_code != 204:
		raise ValueError(
			f'Verification failed. HTTP status code {request.status_code}' +
			'\n- ' + '\n- '.join(request.json()['errors'][''])
		)
	print(f'Login successful')
	return True

def verify_login_status(exception = True) -> bool:
	'''Check if we are logged in to **DB.'''

	print(f'Verifying login status for {URL_SERVER}')
	request = session.get(
		f'{URL_SERVER}/api/users/current',
	)
	if request.status_code != 200:
		if exception:
			raise ValueError(f'Verification failed. HTTP status code {request.status_code}')
		else:
			print(f'Verification failed. HTTP status code {request.status_code}')
			return False

	print(f'Logged in as ' + request.json()['name'])
	return True

def save_cookies() -> bool:
	'''Save cookies to disk.'''

	filename = sys.argv[0] + '.cookies.pickle'
	with open(filename, 'wb') as file:
		pickle.dump(session.cookies, file)
	print(f'Cookies saved to {filename}')
	return True

def load_cookies() -> bool:
	'''Load cookies from disk.'''

	try:
		filename = sys.argv[0] + '.cookies.pickle'
		with open(filename, 'rb') as file:
			session.cookies.update(pickle.load(file))
		print(f'Cookies loaded from {filename}')
		return True
	except FileNotFoundError:
		print(f'Cookies not found')
		return False
	except pickle.UnpicklingError:
		print(f'Failed to decode cookies')
		return False
	
# removing tags (for reference)
def remove_entry_tag_usage(
    session: requests.Session, entry_type: str, tag_usage_id: int
):
    deletion_url = f"{URL_SERVER}/api/users/current/{entry_type}Tags/{tag_usage_id}"
    deletion = session.delete(deletion_url)
    deletion.raise_for_status()

# adding tags (the important part)
def add_entry_tag_usage(
    session: requests.Session, entry_type: str, entry_id: int, tag_id: int
):
    addition_url = f"{URL_SERVER}/api/users/current/{entry_type}Tags/{entry_id}"
    addition = session.put(addition_url, params={"additionalNames":"", "id": tag_id, "name":"", "urlSlug":""})
    addition.raise_for_status()

# ----

if not (load_cookies() and verify_login_status(exception = False)):
	login()
	verify_login_status(exception = True)
	save_cookies()

#----

request = session.get(
	f'https://vocadb.net/api/users/16491/profileComments?start=0&getTotalCount=false&maxResults=700&userId=16491',
)
_ = session.get(
	f'{URL_SERVER}/api/antiforgery/token'
)

'''
request_entry_data = session.get(
		f'{URL_SERVER}/api/albums/{album_id}/for-edit'
	)
request_entry_tags = session.get(
	f'{URL_SERVER}/api/albums/{album_id}/tagUsages'
	)

entry_data = request_entry_data.json()
entry_data_modified = request_entry_data.json()

# print entry data
print()
print('----' * 2)
print()
print('url     : ' + f'{URL_SERVER}/Al/{album_id}')
print('name    : ' + entry_data['name'])
print('tags    : ' + ', '.join([tag_usage['tag']['name'] for tag_usage in request_entry_tags.json()['tagUsages']]))

tag_usages = [] # for tag usage deleting
tag_ids = [] # for update notes
for tag_usage in request_entry_tags.json()['tagUsages']:
	tag_usage_id = str(tag_usage['id'])
	tag_id = str(tag_usage['tag']['id'])
	tag_usages.append(tag_usage_id)
	tag_ids.append(tag_id)

print('tag:', tag_usages, tag_ids)
print()
'''

#actually doing the thing
print('add tag usg: test tag')
add_entry_tag_usage(session, "album", ALBUM_ID, TAG_ID)