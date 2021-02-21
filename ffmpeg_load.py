import nuke
import nukescripts
import os
import re
import platform
from distutils.spawn import find_executable

# Check if platform is Windows
def isWindows():
    if platform.system() == 'Windows':
        return True
    else:
        return False

# Define knobChanged
def ffmpeg_knobChanged():
    n = nuke.thisNode()
    k = nuke.thisKnob()
    watch_list = ['inFile', 'outFile', 'prefix', 'fileName', 'suffix', 'env', 'envPath', 'fileType', 'codec', 'colorspace', 'fps', 'crf', 'audio', 'startFrame', 'endFrame', 'limit', 'outPreview']
    input = n['inFile']
    output = n['outFile']
    prefix = n['prefix']
    filename = n['fileName']
    suffix = n['suffix']
    customFFmpeg = n['env']
    ffmpegPath = n['envPath']
    outputPreview = n['outPreview']
    cmdPreview = n['cmdPreview']
    fileType = n['fileType']
    codec = ['libx264', 'libx265']
    colorspace = ['gamma22', 'linear']
    limit = n['limit']

    # Custom ffmpeg path
    if k.name() == 'env':
        if customFFmpeg.value():
            ffmpegPath.setVisible(True)
        else:
            ffmpegPath.setFlag(0x40000)

    # disable knobs if limit frane range is not checked
    if k.name() == 'limit':
        if not limit.value():
            for knob in ['startFrame', 'endFrame']:
                n[knob].setFlag(0x80)
        else:
            for knob in ['startFrame', 'endFrame']:
                n[knob].clearFlag(0x80)
                # set first and last frame
                n['startFrame'].setValue(n.input(0)['first'].value())
                n['endFrame'].setValue(n.input(0)['last'].value())

    #Set values when input gets connected
    if n.input(0) and os.path.isfile(n.input(0)['file'].evaluate()):
        if not input.value():
            input.setValue(nukescripts.replaceHashes(nuke.filename(n.input(0))))
        if not output.value():
            output.setValue(os.path.dirname(nukescripts.replaceHashes(input.value()))+'/')
        if not filename.value():
            filename.setValue(re.sub(r'.%.*d.exr', "", os.path.basename(nukescripts.replaceHashes(input.value()))))

    #set output preview
    outputPreview.setValue(''.join((output.value()+prefix.value(), filename.value(), suffix.value(), '.',  fileType.value())))

    #Set command preview
    if k.name() in watch_list:
        # watch changes and adjust output

        # Check if use custom ffmpeg path and start compiling command
        if customFFmpeg.value() and os.path.isfile(ffmpegPath.value()):
            ffmpegPath = ffmpegPath.value()
        else:
            ffmpegPath = 'ffmpeg'

        if n['audio'].value():
            audioPath = '"%s"' % os.path.abspath(n['audio'].evaluate())
        else:
            audioPath = None
        inputPath = '"%s"' % os.path.abspath(input.value())
        outputPath = '"%s"' % os.path.abspath(outputPreview.value())
        startFrame = int(n['startFrame'].value())
        endFrame = int(n['endFrame'].value())
        framerange = endFrame - startFrame + 1

        args = '%s%s -apply_trc %s -framerate %s -start_number %s -i %s -c:v %s%s -crf %s -pix_fmt yuv420p %s' % (ffmpegPath,
                                                                                                                  '' if not n['audio'].value() is None else (' -i %s' % audioPath),
                                                                                                                  colorspace[int(n['colorspace'].getValue())],
                                                                                                                  str(n['fps'].value()),
                                                                                                                  str(startFrame),
                                                                                                                  inputPath,
                                                                                                                  codec[int(n['codec'].getValue())],
                                                                                                                  '' if not n['limit'].value() else ' -frames:v %s' % str(framerange),
                                                                                                                  str(int(n['crf'].value())),
                                                                                                                  outputPath
                                                                                                                  )
        cmdPreview.setValue(args)

def ffmpeg_execute():
    def isNot_exec(name):
        #check whether terminal program exists
        return find_executable(name) is None

    def findTerminal():
        termList = ["x-terminal-emulator", "konsole", "gnome-terminal", "urxvt", "rxvt", "termit", "terminator", "Eterm", "aterm", "uxterm", "xterm", "roxterm", "xfce4-terminal", "termite", "lxterminal", "mate-terminal", "terminology", "st", "qterminal", "lilyterm", "tilix", "terminix", "kitty", "guake", "tilda", "alacritty", "hyper"]
        #list taken from https://github.com/i3/i3/blob/next/i3-sensible-terminal
        i = 0
        for term in termList:
            if isNot_exec(term):
                i += 1
            else:
                break
        return termList[i]

    n = nuke.thisNode()
    args = n['cmdPreview'].value()

    if isWindows():
        start = 'start cmd /k %s' % args
    else:
        start = "%s -e %s" % (findTerminal(), args)

    if args:
        os.popen(start)
    else:
        nuke.message('Settings incomplete!')

def ffmpeg_clear():
    node = nuke.thisNode()
    knobs = ['inFile', 'outFile', 'prefix', 'fileName', 'suffix', 'audio', 'outPreview', 'cmdPreview']
    for knob in ['startFrame', 'endFrame', 'limit']:
        node[knob].setValue(0)
    for knob in knobs:
        node[knob].setValue('')
