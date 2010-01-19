import sys
import os
import gtk
import pygtk
import re
import tempfile
import urllib2
from imdb import IMDb

class nfo_gui:
	wTree = gtk.Builder()

	def __init__(self):
		# Setup GUI from file
		self.builder = gtk.Builder()
		self.builder.add_from_file("nfo_builder.glade")
		self.window = self.builder.get_object("main_window")
		if self.window:
			self.window.connect("destroy", gtk.main_quit)
		else:
			print "Can't get main window"
			exit(0)

		# Setup tree stores for displaying folder contents and search results
		self.contents_store = gtk.TreeStore(str);
		self.search_store = gtk.TreeStore(str)


		# Set default path for movies
		self.filechooser = self.builder.get_object('filechooser')
		self.filechooser.set_current_folder(os.getenv("HOME"))
		self.filechooser.connect("current_folder_changed", self.populate_folder_view)

		# Setup file viewer
		fv = self.builder.get_object('folder_view')
		col = gtk.TreeViewColumn("Folder")
		coll_cell_text = gtk.CellRendererText()
		col.pack_start(coll_cell_text, True)
		col.add_attribute(coll_cell_text, "text", 0)
		self.fill_contents_store(os.getenv("HOME"))
		fv.set_model(self.contents_store)
		fv.append_column(col)
		fv.connect("row-activated", self.select_folder)

		# Setup search viewer
		sv = self.builder.get_object('search_view')
		col = gtk.TreeViewColumn("Search Results")
		col_cell_text = gtk.CellRendererText()
		col.pack_start(col_cell_text, True)
		col.add_attribute(col_cell_text, "text", 0)
		sv.set_model(self.search_store)
		sv.append_column(col)
		sv.connect('cursor-changed', self.view_search)
		sv.connect('row-activated', self.movie_search_selected)

		# Setup seach button
		self.search_button = self.builder.get_object('search_button')
		self.search_button.connect_after("clicked", self.imdb_search)

		
		self.fanart = self.builder.get_object('fanart')
		self.fanart_image = self.builder.get_object('fanart_image')
		self.search_view = self.builder.get_object('search_view')
		self.title_entry = self.builder.get_object('title_entry')
		self.imdb_entry = self.builder.get_object('imdb_entry')
		self.runtime_entry = self.builder.get_object('runtime_entry')
		self.rating_entry = self.builder.get_object('rating_entry')
		self.year_entry = self.builder.get_object('year_entry')
		self.studio_entry = self.builder.get_object('studio_entry')
		self.director_entry = self.builder.get_object('director_entry')
		self.cast_entry = self.builder.get_object('cast_entry')
		self.genre_entry = self.builder.get_object('genre_entry')
		self.tagline_entry = self.builder.get_object('tagline_entry')
		self.outline_entry = self.builder.get_object('outline_entry')
		self.plot_entry = self.builder.get_object('plot_entry')
		self.imdb = IMDb(accessSystem='http', adultSearch=0)
		self.poster_image = self.builder.get_object('poster_image')
		self.statusbar = self.builder.get_object('statusbar')
		self.status_context = self.statusbar.get_context_id("my status")
		self.previous_cursor = -1
		self.page_opener = urllib2.build_opener()

	def movie_search_selected(self, sv, three, four):
		print 'movie_search_selected'
		num = sv.get_cursor()[0][0]
		movie = self.current_search_results[num]
		id = movie.movieID
		url = "http://api.themoviedb.org/2.1/Movie.imdbLookup/en/xml/4acde11346efa422a66666b90fea1cd0/tt" + str(id)
		print url
		page = self.page_opener.open(url)
		xml = page.read()
		print xml


	def view_search(self, sv):
		print 'view_search'
		num = sv.get_cursor()[0][0]
		if self.previous_cursor == num:
			return
		self.previous_cursor = num
		movie = self.current_search_results[num]
		self.statusbar.push(self.status_context, "Searching for movie " + movie['smart canonical title']);
		movie = self.imdb.get_movie(movie.movieID)
		self.imdb.update(movie, info=('taglines',))

		# title
		if 'smart canonical title' in movie.keys():
			self.title_entry.set_text(movie['smart canonical title'])
		else:
			self.title_entry.set_text('')

		self.imdb_entry.set_text(movie.movieID)

		# plot
		if 'plot' in movie.keys():
			self.plot_entry.get_buffer().set_text(movie['plot'][0].partition('::')[0])
		else:
			self.plot_entry.get_buffer().set_text('')

		# director
		if 'director' in movie.keys():
			self.director_entry.set_text(movie['director'][0]['name'])
		else:
			self.director_entry.set_text('')

		# year
		if 'year' in movie.keys():
			self.year_entry.set_text(str(movie['year']))
		else:
			self.year_entry.set_text('')

		# genre
		if 'genres' in movie.keys():
			genres = ', '.join("%s" % genre for genre in movie['genres'])
			self.genre_entry.set_text(genres)
		else:
			self.genre_entry.set_text('')

		# Rating
		if 'certificates' in movie.keys():
			ratings = ''
			for certificate in movie['certificates']:

				m = re.search('USA:', certificate)
				if m:
					if ratings == '':
						ratings += certificate.partition('::')[0]
					else:
						ratings += ',' + certificate.partition('::')[0]
			self.rating_entry.set_text(ratings)
		else:
			self.rating_entry.set_text('')

		# runtime
		if 'runtimes' in movie.keys():
			self.runtime_entry.set_text(str(movie['runtimes'][0]))
		else:
			self.runtime_entry.set_text('')

		# image preview
		if 'cover url' in movie.keys():
			local_file = '/tmp/' + movie.movieID + '.jpg'
			if os.path.exists(local_file):
				self.poster_image.set_from_file(local_file)
			else:
				cmd = 'wget ' + movie['cover url'] + ' -O ' + local_file
				os.system(cmd)
				self.poster_image.set_from_file(local_file)
		else:
			self.poster_image.clear()

		# outline
		if 'plot outline' in movie.keys():
			self.outline_entry.set_text(movie['plot outline'])
		else:
			self.outline_entry.set_text('')

		# tagline
		if 'taglines' in movie.keys():
			self.tagline_entry.set_text(movie['taglines'][0])
		else:
			self.tagline_entry.set_text('')

		# cast
		if 'cast' in movie.keys():
			cast = movie['cast']
			cast = ', '.join("%s" % c['name'] for c in movie['cast'][0:4])
			self.cast_entry.set_text(cast)
		else:
			self.cast_entry.set_text('')

		# studio
		if 'production companies' in movie.keys():
			companies = ', '.join("%s" % c for c in movie['production companies'])
			self.studio_entry.set_text(companies)
		else:
			self.studio_entry.set_text("")

		# clear status bar
		self.statusbar.pop(self.status_context);

	def imdb_search(self, button):
		search_text = self.title_entry.get_text()
		if search_text == '':
			return
		self.current_search_results = self.imdb.search_movie(search_text)
		self.search_store.clear()
		for result in self.current_search_results:
			self.search_store.append(None, [result])
		self.fanart.hide()
		self.search_view.show()
		

	def select_folder(self, fv, col_num, four):
		num = col_num[0]
		t = self.contents_store[num][0]
		self.title_entry.set_text(t)

		
	def fill_contents_store(self, path):
		self.contents_store.clear()
		#img = gtk.icon_theme_get_default().load_icon('folder', gtk.ICON_SIZE_MENU, 0)
		for f in os.listdir(path):
			fullname = os.path.join(path, f)
			is_dir = os.path.isdir(fullname)
			is_hidden = True if f[0] == '.' else False
			if is_dir and not is_hidden:
				self.contents_store.append(None, [f])

	def populate_folder_view(self, fc):
		fv = self.builder.get_object("folder_view")
		#print fc.get_current_folder()
		#print fc.get_current_folder_file()
		#print fc.get_title()
		self.fill_contents_store(fc.get_current_folder())
		fv.set_model(self.contents_store)


gui = nfo_gui()
if gui == None:
	print "Can't load gui from file"
	exit(0)

gui.window.show()
gtk.main()

# -identify -frames 0 -vc null -vo null -ao null"
