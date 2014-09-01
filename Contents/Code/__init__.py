TITLE = 'DR TV'
PREFIX_VIDEO = '/video/drdk'
PREFIX_AUDIO = '/audio/drdk'
API_URL = 'http://www.dr.dk/mu-online/api/'
ART = 'art-default.jpg'
ICON = 'icon-default.png'
WebsiteURL = 'http://www.dr.dk'
WebsiteTVURL = 'http://www.dr.dk/tv'
API_VERSION = "1.1"
menuTitles = {'TopSpots':'Anbefalede', 'PopularList':'Populære','Live':'Live TV', 'News':'Nyheder', 'SelectedList':'Udvalgte','LastChance':'Sidste chance'}

def Start():
	pass
	
@handler(PREFIX_VIDEO, TITLE, art = ART, thumb=ICON)
def MainMenu():
	Data.SaveObject('allDrLive',JSON.ObjectFromURL('http://www.dr.dk/mu-online/api/1.1/channel/all-active-dr-tv-channels'))
	oc = ObjectContainer()
	frontJSON = JSON.ObjectFromURL(API_URL + API_VERSION + '/page/tv/front')
	# ToCarusel
	for frontPage in frontJSON:
		if 'Items' in frontJSON[frontPage]:
			oc.add(DirectoryObject(title = unicode(menuTitles[frontPage]), thumb = R(ICON), key = Callback(subMenu, json = frontJSON[frontPage], title = unicode(menuTitles[frontPage]))))
		else:
			oc.add(DirectoryObject(title = unicode(menuTitles[frontPage]), thumb = R(ICON), key = Callback(liveMenu, json = frontJSON[frontPage], title = unicode(menuTitles[frontPage]))))
			
	
	return oc
	
@route(PREFIX_VIDEO +'/submenu', json = JSON)
def subMenu(json, title):
	oc = ObjectContainer(title1 = title, title2 = '', no_history = True)
	if 'Previous' in json['Paging']:
		oc.add(DirectoryObject(title = 'Forrige', key = Callback(subMenu, json = JSON.ObjectFromURL(json['Paging']['Previous']))))
	for items in json['Items']:
		oc.add(EpisodeObject(title = items['Title'], thumb = items['PrimaryImageUri'], url = WebsiteTVURL + '/se/' + items['SeriesSlug'] + '/' + items['Slug']))
		Log.Debug(items)
	if 'Next' in json['Paging']:
		oc.add(NextPageObject(title = 'Mere', key = Callback(subMenu, json = JSON.ObjectFromURL(json['Paging']['Next']))))
	
	
	return oc
@route(PREFIX_VIDEO +'/livemenu', json = JSON)
def liveMenu(json, title):
	oc = ObjectContainer(title1 = title, title2 = '', no_history = True)
	liveJson = Data.LoadObject('allDrLive')
	for live in json:
		title = ''
		thumb = R(ICON)
		for titleJson in liveJson:
			if titleJson['Slug'] == live['ChannelSlug']:
				title = titleJson['Title']
				thumb = titleJson['PrimaryImageUri']
				continue
		oc.add(VideoClipObject(title = title, thumb = thumb , url = WebsiteTVURL + '/live/' + live['ChannelSlug']))
	return oc