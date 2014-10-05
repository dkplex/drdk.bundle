NAME = 'DR TV'
PREFIX_VIDEO = '/video/drdk'
PREFIX_AUDIO = '/music/drdk'
API_URL = 'http://www.dr.dk/mu-online/api/'
ART = 'art-default.jpg'
ICON = 'icon-default.png'
WebsiteURL = 'http://www.dr.dk'
WebsiteTVURL = 'http://www.dr.dk/tv'
API_VERSION = "1.1"

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
	oc.title2 = L('Frontpage')
	json = JSON.ObjectFromURL(API_URL + API_VERSION + '/page/tv/front')
	for FrontpageViewModel in json:
		if 'ServiceMessage' in FrontpageViewModel:
			
			oc.header = unicode(json['ServiceMessage']['Title'])
			oc.message = json['ServiceMessage']['Message']
		elif 'Live' in FrontpageViewModel:
			oc.add(DirectoryObject(title = unicode(L(FrontpageViewModel)), key = Callback(live)))
		elif 'Themes' in FrontpageViewModel:
			for themes in json[FrontpageViewModel]:
				oc.add(DirectoryObject(title = unicode(themes['Title'])), key = Callback(MuList, sourceURL = themes['Paging']['Source']))
		else:
			oc.add(DirectoryObject(title = unicode(L(FrontpageViewModel)), key = Callback(MuList, sourceURL  = json[FrontpageViewModel]['Paging']['Source']) ))
	oc.add(DirectoryObject(title = unicode(L('Programmer')), thumb = R(ICON), key = Callback(programs)))
	oc.add(SearchDirectoryObject(identifier="com.plexapp.plugins.drdk", title=unicode(L("Søg efter programmer")), prompt=unicode(L("Søg efter...")), thumb=R(ICON)))
	oc.add(PrefsObject(title = unicode( L('Indstillinger')), thumb = R(ICON)))
	return oc

@route( PREFIX_VIDEO + '/live')
def live():
	oc = ObjectContainer(title1 = unicode(L('Live')), title2 = unicode(L("Choose Channel")))
	liveChannels = Data.LoadObject('drFront')['Live']
	channelTitles = Data.LoadObject('channelTitles')
	for channels in liveChannels:
		oc.add(PopupDirectoryObject(title = channelTitles[channels['ChannelSlug']]['Title'], thumb = channelTitles[channels['ChannelSlug']]['PrimaryImageUri'], key = Callback(livePlayMenu, slug = channels['ChannelSlug'] ) ))
	return oc

@route(PREFIX_VIDEO + '/livePlayMenu')
def livePlayMenu(slug):
	oc = ObjectContainer(mixed_parents = True)
	channelTitles = Data.LoadObject('channelTitles')
	json = JSON.ObjectFromURL(API_URL + API_VERSION + '/page/tv/children/live/'  + slug)
	oc.title1 = unicode(L('Live'))
	oc.title2 = channelTitles[json['NowNext']['ChannelSlug']]['Title']
	oc.add(VideoClipObject(title = unicode(L('Live') + ': ' + channelTitles[json['NowNext']['ChannelSlug']]['Title']), thumb = channelTitles[json['NowNext']['ChannelSlug']]['PrimaryImageUri'], url = WebsiteTVURL + '/live/' + json['NowNext']['ChannelSlug']))
	oc.add(DirectoryObject(title = unicode(L('SelectedList')), thumb = R(ICON), key = Callback(MuList, sourceURL = json['SelectedList']['Paging']['Source'])))
	oc.add(DirectoryObject(title = unicode(L('Programmer')), thumb = R(ICON), key = Callback(MuList, sourceURL = json['Programs']['Paging']['Source'])))
	
	return oc

@route(PREFIX_VIDEO + '/MuList', hidePlayMenu = bool)
def MuList(sourceURL, hidePlayMenu = False):
	oc = ObjectContainer()
	json = JSON.ObjectFromURL(sourceURL)
	for items in json['Items']:
		if hidePlayMenu ==True:
			oc.add(EpisodeObject(title = unicode(items['Title']), thumb = items['PrimaryImageUri'], url = WebsiteTVURL + '/se/' + items['SeriesSlug'] + '/' + items['Slug']))
		else:
			oc.add(PopupDirectoryObject(title = unicode( items['SeriesTitle']), thumb = items['PrimaryImageUri'], key = Callback(ondemandPlayMenu, slug = items['Slug'], seriesslug = items['SeriesSlug'], channelslug = items['PrimaryChannelSlug'])))
	if 'Next'  in json['Paging']:
		oc.add(NextPageObject(title = unicode(L('Flere')), thumb = R(ICON), key = Callback(MuList, sourceURL = json['Paging']['Next'])))
	return oc

@route(PREFIX_VIDEO + '/ondemandPlayMenu')
def ondemandPlayMenu(slug, seriesslug, channelslug):
	oc = ObjectContainer(mixed_parents = True)
	json = JSON.ObjectFromURL(API_URL + API_VERSION + '/page/tv/children/player/' + slug + '?seriesid=' + seriesslug + '&channel=' + channelslug)
	oc.add(EpisodeObject(title = unicode(L('Play') + ': ' + json['ProgramCard']['Title']), thumb = json['ProgramCard']['PrimaryImageUri'], url = WebsiteTVURL + '/se/' + json['ProgramCard']['SeriesSlug'] + '/' + json['ProgramCard']['Slug']))
	if json['SelectedList']['TotalSize'] >0:
		oc.add(DirectoryObject(title = unicode(json['SelectedList']['Title']), thumb = R(ICON), key = Callback(MuList, sourceURL = json['SelectedList']['Paging']['Source'], hidePlayMenu = True)))
	if json['RelationsList']['TotalSize'] > 0:
		oc.add(DirectoryObject(title = unicode(L('RelationsList')), thumb = R(ICON), key = Callback(MuList, sourceURL = json['RelationsList']['Paging']['Source'], hidePlayMenu = True)))
	if json['Programs']['TotalSize'] > 0:
		oc.add(DirectoryObject(title = unicode(L('Programs')), thumb = R(ICON), key = Callback(MuList, sourceURL = json['Programs']['Paging']['Source'], hidePlayMenu = True)))
		
	
	return oc
@route(PREFIX_VIDEO + '/programs')
def programs():
	oc = ObjectContainer()
	if Prefs['ProgramShowStyle'] == 'Alle kanaler (hurtig)':
		json = JSON.ObjectFromURL( API_URL + API_VERSION +'/page/tv/children/front/*')['Indexes']
		for channels in json:
			oc.add(DirectoryObject(title = channels['Title'], thumb = R(ICON), key = Callback(MuList, sourceURL = channels['Source'].replace('?channels=*',''))))
	else:
		drFront = Data.LoadObject('drFront')['Live']
		channelTitles = Data.LoadObject('channelTitles')
		for channels in drFront:
			oc.add(DirectoryObject(title = unicode( channelTitles[channels['ChannelSlug']]['Title']), thumb = channelTitles[channels['ChannelSlug']]['PrimaryImageUri'], key = Callback (programIndexes, slug =  channels['ChannelSlug'])))

	return oc

@route(PREFIX_VIDEO + '/programIndexes')
def programIndexes(slug):
	oc = ObjectContainer()
	json = JSON.ObjectFromURL(API_URL + API_VERSION + '/page/tv/children/front/' + slug )
	for indexes in json['Indexes']:
		if indexes['TotalSize'] > 0:
			oc.add(DirectoryObject(title = indexes['Title'], key = Callback(MuList, sourceURL = indexes['Source'])))
	Log.Debug(slug)
	return oc