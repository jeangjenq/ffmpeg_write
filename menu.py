#Create toolbar with icon
JJmenu = nuke.menu('Nodes').addMenu('jj_tools', icon='icon_JJ.png')

filepath = os.path.join(os.path.dirname(__file__), "ffmpeg_write.nk")
JJmenu.addCommand('ffmpeg_write', 'nuke.loadToolset(filepath)')
