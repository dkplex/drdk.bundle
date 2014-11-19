NAME = 'DR TV'
PREFIX_VIDEO = '/video/drdk'
PREFIX_AUDIO = '/music/drdk'
API_URL = 'http://www.dr.dk/mu-online/api/'
ART = 'art-default.jpg'
ICON = 'icon-default.png'
WebsiteURL = 'http://www.dr.dk'
WebsiteTVURL = 'http://www.dr.dk/tv'
API_VERSION = "1.1"

####################################################################################################
def Start():
	Data.SaveObject('allDrTVLive',JSON.ObjectFromURL(API_URL + API_VERSION +'/channel/all-active-dr-tv-channels'))
	Data.SaveObject('drFront', JSON.ObjectFromURL(API_URL + API_VERSION +'/page/tv/front'))
	channelTitles = {}
	for channels in Data.LoadObject('allDrTVLive'):
		channelTitles[channels['Slug']] = {'Title': channels['Title'], 'PrimaryImageUri':channels['PrimaryImageUri']}
	Data.SaveObject('channelTitles', channelTitles)

####################################################################################################	
@handler(PREFIX_VIDEO, NAME)
def MainMenu():
	oc = ObjectContainer()
	oc.title1 = NAME
	oc.title2 = NAME
	json = JSON.ObjectFromURL(API_URL + API_VERSION + '/page/tv/front')

	if 'ServiceMessage' in json:
		
		oc.header = unicode(json['ServiceMessage']['Title'])
		oc.message = json['ServiceMessage']['Message']

	if json['SelectedList']['TotalSize'] >0:
		for items in json['SelectedList']['Items']:
			oc.add(PopupDirectoryObject(title = unicode(items['Title']),
									tagline = items['Subtitle'], 
									thumb = items['PrimaryImageUri'], 
									key = Callback(ondemandPlayMenu, 
												slug = items['Slug'], 
												seriesslug = items['SeriesSlug'])))
		oc.add(DirectoryObject(title = unicode(L('SelectedList')), 
							thumb = R(ICON), 
							key = Callback(MuList, 
										sourceURL = json['SelectedList']['Paging']['Source'])))
	oc.add(DirectoryObject(thumb = R(ICON), 
						title = unicode(L('Live')), 
						key = Callback(live)))
	if 'Themes' in json:
		for themes in json['Themes']:
				oc.add(DirectoryObject(thumb = R(ICON), 
									title = unicode(themes['Title']), 
									key = Callback(MuList, 
												sourceURL = themes['Paging']['Source'])))
	if json['PopularList']['TotalSize']>0:
		oc.add(DirectoryObject(title = unicode(L('PopularList')), 
							thumb = R(ICON), 
							key = Callback(MuList, 
										sourceURL = json['PopularList']['Paging']['Source'])))
	if json['PopularList']['TotalSize'] >0:
		oc.add(DirectoryObject(title = unicode(L('PopularList')), 
							thumb = R(ICON), 
							key = Callback(MuList, 
										sourceURL = json['TopSpots']['Paging']['Source'])))
	if json['LastChance']['TotalSize'] >0:
		oc.add(DirectoryObject(title = unicode(L('LastChance')), 
							thumb = R(ICON), 
							key = Callback(MuList, 
										sourceURL = json['LastChance']['Paging']['Source'])))
	if json['News']['TotalSize'] >0:
		oc.add(DirectoryObject(title = unicode(L('News')), 
							thumb = R(ICON), 
							key = Callback(MuList, 
										sourceURL = json['News']['Paging']['Source'])))
	oc.add(DirectoryObject(title = unicode(L('Programmer')), 
						thumb = R(ICON), 
						key = Callback(programs)))
	oc.add(SearchDirectoryObject(identifier="com.plexapp.plugins.drdk", 
								title=unicode(L("Søg efter programmer")), 
								prompt=unicode(L("Søg efter...")), 
								thumb=R(ICON)))
	oc.add(PrefsObject(title = unicode( L('Indstillinger')), 
					thumb = R(ICON)))
	return oc

####################################################################################################
@route( PREFIX_VIDEO + '/live')
def live():
	oc = ObjectContainer(title1 = unicode(L('Live')), 
						title2 = unicode(L("Choose Channel")))
	liveChannels = Data.LoadObject('drFront')['Live']
	channelTitles = Data.LoadObject('channelTitles')
	for channels in liveChannels:
		oc.add(PopupDirectoryObject(title = channelTitles[channels['ChannelSlug']]['Title'], 
								thumb = channelTitles[channels['ChannelSlug']]['PrimaryImageUri'], 
								key = Callback(livePlayMenu, slug = channels['ChannelSlug'] ) ))
	return oc

####################################################################################################
@route(PREFIX_VIDEO + '/livePlayMenu')
def livePlayMenu(slug):
	oc = ObjectContainer(mixed_parents = True, 
						title1 = unicode(L('Live')))
	channelTitles = Data.LoadObject('channelTitles')
	json = JSON.ObjectFromURL(API_URL + API_VERSION + '/page/tv/live/'  + slug)
	oc.title2 = channelTitles[json['NowNext']['ChannelSlug']]['Title']
	oc.add(VideoClipObject(title = unicode(L('Live') + ': ' + channelTitles[json['NowNext']['ChannelSlug']]['Title']), 
						thumb = channelTitles[json['NowNext']['ChannelSlug']]['PrimaryImageUri'], 
						url = WebsiteTVURL + '/live/' + json['NowNext']['ChannelSlug']))
	
	## Timemachine start @todo, enable timeshift of live
# 	TMNow = False
# 	TMNext = False
# 	for next in json['NowNext']['Next']:
# 		if next['ProgramCardHasPrimaryAsset']:
# 			TMNext = True
# 			break
# 	if json['NowNext']['Now']['ProgramCardHasPrimaryAsset']:
# 		TMNow = True
# 	
# 	if TMNow or TMNext:
# 		do = DirectoryObject()
	
	if json['SelectedList']['TotalSize'] > 0:
		oc.add(DirectoryObject(title = unicode(L('SelectedList')), 
							thumb = R(ICON), 
							key = Callback(MuList, 
										sourceURL = json['SelectedList']['Paging']['Source'])))
	if json['TopSpots']['TotalSize']>0:
		oc.add(DirectoryObject(title = unicode(L('TopSpots')), 
							thumb = R(ICON), 
							key = Callback(MuList, 
										sourceURL = json['TopSpots']['Paging']['Source'])))
	if json['PopularList']['TotalSize']>0:
		oc.add(DirectoryObject(title = unicode(L('PopularList')), 
							thumb = R(ICON), 
							key = Callback(MuList, 
										sourceURL = json['PopularList']['Paging']['Source'])))
		
		
	return oc

####################################################################################################
@route(PREFIX_VIDEO + '/MuList')
def MuList(sourceURL):
	oc = ObjectContainer()
	json = JSON.ObjectFromURL(sourceURL)
	for items in json['Items']:
		oc.add(PopupDirectoryObject(title = unicode( items['Title']), 
								thumb = items['PrimaryImageUri'], 
								summary = items['Subtitle'],
								key = Callback(ondemandPlayMenu, 
											slug = items['Slug'], 
											seriesslug = items['SeriesSlug'])))
	if 'Next'  in json['Paging']:
		oc.add(NextPageObject(title = unicode(L('Flere')), 
							thumb = R(ICON), 
							key = Callback(MuList, 
										sourceURL = json['Paging']['Next'])))
	return oc

####################################################################################################
@route(PREFIX_VIDEO + '/ondemandPlayMenu')
def ondemandPlayMenu(slug, seriesslug):
	oc = ObjectContainer(mixed_parents = True)
	json = JSON.ObjectFromURL(API_URL + API_VERSION + '/page/tv/player/' + slug + '?seriesid=' + seriesslug)
	oc.add(EpisodeObject(originally_available_at =Datetime.ParseDate(json['ProgramCard']['PrimaryBroadcastStartTime']) , 
						duration = json['ProgramCard']['PrimaryAsset']['DurationInMilliseconds'], 
						title = unicode(L('Play') + ':' + json['ProgramCard']['Title']), 
						thumb = json['ProgramCard']['PrimaryImageUri'], 
						summary = json['ProgramCard']['PrimaryImageUri'], 
						show = unicode( json['ProgramCard']['SeriesTitle']),
						url = WebsiteTVURL + '/se/' + json['ProgramCard']['SeriesSlug'] + '/' + json['ProgramCard']['Slug']))
	if json['TopSpots']['TotalSize'] > 0:
		oc.add(DirectoryObject(title = unicode(L('TopSpots')), 
							thumb = R(ICON), 
							key = Callback(MuList, 
										sourceURL = json['TopSpots']['Paging']['Source'])))
	if json['SelectedList']['TotalSize'] > 0:
		oc.add(DirectoryObject(title = unicode(L('SelectedList')), 
							thumb = R(ICON), 
							key = Callback(MuList, 
										sourceURL = json['SelectedList']['Paging']['Source'])))
	if json['RelationsList']['TotalSize'] > 1:
		oc.add(DirectoryObject(title = unicode(L('RelationsList')), 
							thumb = R(ICON), 
							key = Callback(MuList, 
										sourceURL = json['RelationsList']['Paging']['Source']) ))
	if json['PopularList']['TotalSize'] > 0:
		oc.add(DirectoryObject(title = unicode(L('PopularList')), 
							thumb = R(ICON), 
							key = Callback(MuList, 
										sourceURL = json['PopularList']['Paging']['Source'])))	
	return oc

####################################################################################################
@route(PREFIX_VIDEO + '/programs')
def programs():
	oc = ObjectContainer()
	if Prefs['ProgramShowStyle'] == 'Alle kanaler (hurtig)':
		json = JSON.ObjectFromURL( API_URL + API_VERSION +'/page/tv/children/front/*')['Indexes']
		for channels in json:
			oc.add(DirectoryObject(title = channels['Title'], 
								thumb = R(ICON), 
								key = Callback(MuList, 
											sourceURL = channels['Source'].replace('?channels=*',''))))
	else:
		drFront = Data.LoadObject('drFront')['Live']
		channelTitles = Data.LoadObject('channelTitles')
		for channels in drFront:
			oc.add(DirectoryObject(title = unicode( channelTitles[channels['ChannelSlug']]['Title']), 
								thumb = channelTitles[channels['ChannelSlug']]['PrimaryImageUri'], 
								key = Callback (programIndexes, 
											slug =  channels['ChannelSlug'])))

	return oc

####################################################################################################
@route(PREFIX_VIDEO + '/programIndexes')
def programIndexes(slug):
	oc = ObjectContainer()
	json = JSON.ObjectFromURL(API_URL + API_VERSION + '/page/tv/children/front/' + slug )
	for indexes in json['Indexes']:
		if indexes['TotalSize'] > 0:
			oc.add(DirectoryObject(title = indexes['Title'], 
								key = Callback(MuList, 
											sourceURL = indexes['Source'])))
	return oc