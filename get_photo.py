import flickr_api
import pickle
import os

# returns the urls of all photos in an album
def get_photos_url(photos):
	lista_url = []
	for photo in photos:
		lista_url.append(photo.getPhotoFile('Medium'))
	return lista_url

def give_me_photos():
	if not os.path.exists('album.pickle'):
		return ([], [])

	fp1 = file('album.pickle', 'rb')
	fp2 = file('photos.pickle', 'rb')
	album = pickle.load(fp1)
	photos = pickle.load(fp2)
	return (album, photos) 	

def save_photos():
	data = flickr_reader()
	album, photos = data	
	fp1 = file('album.pickle', 'wb')
	fp2 = file('photos.pickle', 'wb')
	pickle.dump(album, fp1)
	pickle.dump(photos, fp2)
	fp1.close()
	fp2.close()

#scarica i miei dati da Flickr
def flickr_reader():
	user = flickr_api.Person.findByUserName('camillathecat')
	photosets = user.getPhotosets()

	lista_album = []
	for album in photosets:
		lista_album.append(album)

	all_photos = {}
	for album in lista_album:
		all_photos[album.title] = get_photos_url(album.getPhotos())
	
	return [lista_album, all_photos]



if __name__ == '__main__':
	save_photos()
