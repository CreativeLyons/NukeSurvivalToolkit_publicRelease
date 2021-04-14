
![NukeSurvivalToolkit-TonyLyons](https://user-images.githubusercontent.com/46404545/93950690-76be2e00-fd44-11ea-96a6-07070b28df81.jpg)

# Nuke Survival Toolkit

[Intro and Installation Video](https://youtu.be/MQq9GH3SekA)

For full online documentation and tool index, visit:

[Nuke Survival Toolkit Documentation](https://docs.google.com/document/d/1eyh2JIecaphItZeq0uuGxlqoASuXNQy1leJGqFI-EeU/edit?usp=sharing)

The Nuke Survival Toolkit is a portable tool menu for the Foundry’s Nuke with a hand-picked selection of nuke gizmos collected from all over the web, organized into 1 easy to install toolbar.

Here’s how to install and use the Nuke Survival Toolkit: 

1.) Download the .zip folder from the Nuke Survival Toolkit github website.  

https://github.com/CreativeLyons/NukeSurvivalToolkit_publicRelease/releases/latest

This github will have all of the up to date changes, bug fixes, tweaks, additions, etc. So feel free to watch or star the github, and check back regularly if you’d like to stay up to date.

2.) Copy or move the NukeSurvivalToolkit Folder either in your User/.nuke/ folder for personal use, or for use in a pipeline or to share with multiple artists, place the folder in any shared and accessible network folder.

3.) Open your init.py file in your /.nuke/ folder into any text editor (or create a new init.py in your User/.nuke/ directory if one doesn’t already exist)

4.) Copy the following code into your init.py file:

```
nuke.pluginAddPath("Your/NukeSurvivalToolkit/FolderPath/Here")
```

5.) Copy the filepath location of where you placed your NukeSurvivalToolkit.  Replace the
Your/NukeSurvivalToolkit/FolderPath/Here text with your NukeSurvivalToolkit filepath location, making sure to keep quotation marks around the filepath.

6.) Save your init.py file, and restart your Nuke session

7.) That’s it! Congrats, you will now see a little red multi-tool in your nuke toolbar.    
