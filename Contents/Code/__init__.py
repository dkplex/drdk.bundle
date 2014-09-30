#from operator import itemgetter

NAME = 'DR TV'
PREFIX_VIDEO = '/video/drdk'
PREFIX_AUDIO = '/music/drdk'
API_URL = 'http://www.dr.dk/mu-online/api/'
ART = 'art-default.jpg'
ICON = 'icon-default.png'
WebsiteURL = 'http://www.dr.dk'
WebsiteTVURL = 'http://www.dr.dk/tv'
API_VERSION = "1.1"
menuTitles = {'Themes':'Tema','TopSpots':'Anbefalede', 'PopularList':'Populære','Live':'Live TV', 'News':'Nyheder', 'SelectedList':'Udvalgte','LastChance':'Sidste chance', 'Now':'Nu','Next':'Næste', 'Programs':'Programmer'}
alphaSlugs = {'A':'a','B':'b','C':'c','D':'d','E':'e','F':'f','G':'g','H':'h','I':'i','J':'j','K':'k','L':'l','M':'m','N':'n','O':'o','P':'p','Q':'q','R':'r','S':'s','T':'t','U':'u','VM':'v..w','XYX': 'x..z',unicode('ÆØÅ'):'æ..å','123':'0..9'}

def Start():
	Data.SaveObject('allDrTVLive',JSON.ObjectFromURL(API_URL + API_VERSION +'/channel/all-active-dr-tv-channels'))
	Data.SaveObject('drFront', JSON.ObjectFromURL(API_URL + API_VERSION +'/page/tv/front'))
	channelTitles = {}
	for channels in Data.LoadObject('allDrTVLive'):
		channelTitles[channels['Slug']] = {'Title': channels['Title'], 'PrimaryImageUri':channels['PrimaryImageUri']}
	Data.SaveObject('channelTitles', channelTitles)
	
@handler(PREFIX_VIDEO, NAME)
def MainMenu():
	
	oc = ObjectContainer()
	oc.title1 = NAME
	oc.title2 = NAME
	json = JSON.ObjectFromURL(API_URL + API_VERSION + '/page/tv/front')
	ShowAllPrograms = False
	for FrontpageViewModel in json:
		
		if 'ServiceMessage' in FrontpageViewModel:
			oc.header = FrontpageViewModel['Title']
			oc.message = FrontpageViewModel['Message']
		elif 'Live' in FrontpageViewModel:
			
			oc.add(DirectoryObject(title = unicode(menuTitles[FrontpageViewModel]), art = R(ART), thumb = R(ICON), key = Callback(live, channelsJSON = json[FrontpageViewModel])))
		elif 'Themes' in FrontpageViewModel:
			for themes in FrontpageViewModel['Themes']:
				oc.add(DirectoryObject(title = unicode(themes['Title'], art = R(ART), thumb = R(ICON), key = Callback(MuList, items = json[FrontpageViewModel]))))
		else:
			oc.add(DirectoryObject(title = unicode(menuTitles[FrontpageViewModel]), art = R(ART), thumb = R(ICON), key = Callback(MuList, items = json[FrontpageViewModel])))
	if Prefs['ProgramShowStyle'] == 'Alle kanaler (Hurtig)':
		oc.add(DirectoryObject(title = unicode( L('Programmer')), thumb = R(ICON), key = Callback(programs, ShowAllPrograms = True,  indexes = JSON.ObjectFromURL(API_URL + API_VERSION +'/page/tv/children/front/*'))))
	else:
		oc.add(DirectoryObject(title = unicode( L('Programmer')), thumb = R(ICON), key = Callback(programs, ShowAllPrograms = False,  indexes = {})))
	
	oc.add(SearchDirectoryObject(identifier="com.plexapp.plugins.drdk", title=unicode(L("Søg efter programmer")), prompt=unicode(L("Søg efter...")), thumb=R(ICON)))
	oc.add(PrefsObject(title = unicode( L('Indstillinger')), thumb = R(ICON)))
	return oc

@route(PREFIX_VIDEO + '/live', channelsJSON = JSON)
def live(channelsJSON):
	oc = ObjectContainer()
	oc.title1 = NAME
	oc.title2 = L('Live')
	channelTitles = Data.LoadObject('channelTitles')
	for channels in channelsJSON:
		oc.add(PopupDirectoryObject(title = unicode( channelTitles[channels['ChannelSlug']]['Title']), art = channelTitles[channels['ChannelSlug']]['PrimaryImageUri'], thumb =  channelTitles[channels['ChannelSlug']]['PrimaryImageUri'] + '?width=512&height=512',  key = Callback(playMenu, jsonURL = API_URL + API_VERSION +'/page/tv/children/live/' + channels['ChannelSlug'])))
	return oc

@route(PREFIX_VIDEO + '/liveMenu')
def playMenu(jsonURL, hidePlayMenu = False):
	oc = ObjectContainer()
	oc.title1 = NAME
	channelTitles = Data.LoadObject('channelTitles')
	json = JSON.ObjectFromURL(jsonURL)
	for items in json:
		if 'NowNext' in items:
			if json[items]['ChannelSlug'] != '*':
				slug = json[items]['ChannelSlug']
				oc.add(VideoClipObject(title = unicode('Live: ' + json[items]['Now']['Title']), url = WebsiteTVURL + '/live/' + slug, thumb = channelTitles[slug]['PrimaryImageUri'] + '?width=512&height=512'))
				for next in json[items]['Next']:
					if next['ProgramCardHasPrimaryAsset']:
						oc.add(DirectoryObject(title = unicode(L('Afspil senere programmer')), thumb = R(ICON), key = Callback(MuScheduleBroadcast, items = json[items])))
						break
		elif 'Channel' in items:
			pass
		elif 'SelectedList' in items:
			oc.add(DirectoryObject(title = unicode(json[items]['Title']), thumb = R(ICON), key = Callback(MuList, items = json[items])))
		elif 'Programs' in items:
			oc.add(DirectoryObject(title = unicode(L('Seneste programmer fra') + ' ' + channelTitles[json[items]['Items'][0]['PrimaryChannelSlug']]['Title']), key = Callback(MuList, items = json[items]), thumb = R(ICON)))
		elif 'ProgramCard' in items:
			oc.add(EpisodeObject(title = unicode(L('Seneste') + ' ' + json[items]['Title']), thumb = json[items]['PrimaryImageUri'], url = WebsiteTVURL + '/se/' + json[items]['SeriesSlug'] + '/' + json[items]['Slug'] ))
		elif 'NextEpisode' in items:
			if 'PrimaryAsset' in json[items]:
				oc.add(EpisodeObject(title = unicode(L('Næste') + ' ' + json[items]['Title']), thumb = json[items]['PrimaryImageUri'], url = WebsiteTVURL + '/se/' + json[items]['SeriesSlug'] + '/' + json[items]['Slug'] ))
		elif 'RelationsList' in items:
			if json[items]['TotalSize'] >1:
				oc.add(DirectoryObject(title = unicode(L('Flere') + ' ' + json[items]['Items'][0]['SeriesTitle']), thumb = R(ICON), key = Callback(MuList, items = json[items], hidePlayMenu = True)))
			else:
				oc.add(EpisodeObject(title = unicode(L('Flere') + ' ' + json[items]['Items'][0]['SeriesTitle'] ), thumb = json[items]['Items'][0]['PrimaryImageUri'], url = WebsiteTVURL + '/se/' + json[items]['Items'][0]['SeriesSlug'] + '/' + json[items]['Items'][0]['Slug'])) 
		elif 'Indexes' in items:
			Log.Debug(items)
		#elif 'Indexes' in items:
		#	Log.Debug('*')
# 			if json['NowNext']['ChannelSlug'] != '*':
# 				slug = 'Alle Kanaler'
# 			else:
			#Log.Debug(items)
			#Log.Debug(json)
			#oc.add(DirectoryObject(title = unicode('Programmer fra ' + title), key = Callback(programs, indexes = json[items])))
			
	
	return oc
@route(PREFIX_VIDEO + '/MuScheduleBroadcast', items = JSON)
def MuScheduleBroadcast(items):
	oc = ObjectContainer()
	oc.title1 = NAME
	for item in items['Next']:
		if item['ProgramCardHasPrimaryAsset']:
			oc.add(EpisodeObject(title = unicode( item['Title']), url = WebsiteTVURL + '/se/' + item['ProgramCard']['SeriesSlug'] + '/' + item['ProgramCard']['Slug'], thumb = item['ProgramCard']['PrimaryImageUri'] ))
	return oc

@route(PREFIX_VIDEO + '/MuList/{items}/{hidePlayMenu}', items = JSON)
def MuList(items, hidePlayMenu = False):
	oc = ObjectContainer()
	oc.title1 = NAME
	for item in items['Items']:
		
		if hidePlayMenu == True:
			oc.add(EpisodeObject(title = unicode( item['Title']), thumb = item['PrimaryImageUri'], url = WebsiteTVURL + '/se/' + item['SeriesSlug'] + '/' + item['Slug']))
		else:
			oc.add(PopupDirectoryObject(title = unicode( item['Title']), thumb = R(ICON), key = Callback(playMenu, jsonURL = API_URL + API_VERSION + '/page/tv/children/player/' + item['Slug'], hidePlayMenu = True)))
		
	if 'Next' in items['Paging']:
		oc.add(NextPageObject(title = unicode(L('Mere...')), key = Callback(MuList, items = JSON.ObjectFromURL(items['Paging']['Next']))))
	return oc

@route(PREFIX_VIDEO + '/programs', indexes = JSON)
def programs(indexes, ShowAllPrograms = False):
	oc = ObjectContainer()
	oc.title1 = NAME
	channelTitles = Data.LoadObject('channelTitles')
	allDrTVLive = Data.LoadObject('allDrTVLive')
	drFront = Data.LoadObject('drFront')
	if ShowAllPrograms == False:
		for channels in drFront['Live']:
			json = JSON.ObjectFromURL(API_URL + API_VERSION +'/page/tv/children/front/' + channels['ChannelSlug'])
			
			oc.add(DirectoryObject(title = unicode(channelTitles[channels['ChannelSlug']]['Title']), thumb = unicode(channelTitles[channels['ChannelSlug']]['PrimaryImageUri']), key = Callback(programs, ShowAllPrograms = True,  indexes = json)))
				
	else:
		for index in indexes['Indexes']:
			if index['TotalSize'] >0:
				oc.add(DirectoryObject(title = unicode(index['Title']), thumb = R(ICON), key = Callback(MuList, items = JSON.ObjectFromURL(index['Source'].replace('?channels=*','')))))
	return oc