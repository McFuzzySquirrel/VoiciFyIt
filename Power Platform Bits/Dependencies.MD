# Power App and Power Automate Dependencies
This lists other enviornment dependencies that are not part of the Power App Solution

## Connectors

You will need to setup the following types of connectors:

- Azure Blob Storage Connector

## SharePoint

You will require a SharePoint Site that you can use 

### Document Libraries

#### Podcasts

This document library will contain all the .mp3 audio files of the generated podcast pulled from container in Azure Blob Storage. These files are displayed in the `Podcasts Screen` of the `Podcaster Demo v3` Canvas App.

**The following columns are recommended**:

- *Title*:
- *Podcast Description*: Used by associated cloud flow: `Podcaster - Process Queue` to populate the podcast description and is used in the gallery view on the `Podcasts Screen` of the `Podcaster Demo v3` Canvas App.
- *Podcast Image*: If you want to display an image in both the gallery view and as image of media player on the `Podcasts Screen` of the `Podcaster Demo v3` Canvas App.

### SharePoint Lists

#### Style Guides

This list contains the styles referenced by the Style drop-down list and is used to set the style in the associated `Create Podcast v3` AI Builder Model. 

**The following columns are recommended**:

- *Title*: This will be the name of the style displaed in the drop-down on the `Welcome Screen` of the `Podcaster Demo v3` Canvas App
- *Style*: Multi line text field that contains the the detailed style guide, this will be used to set the style of the `Create Podcast v3` AI Builder Model

#### Script Submissions

Contains the details of Podcast Script submissions, including original file / text used, script generated and who created the script. This is for audit purposes



