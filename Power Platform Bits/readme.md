# Power Platform App
## Podcaster v3 App
### Welcome Screen
This is where you will set the host names, host voices (from Azure Speech Services), the Style they should follow (this is pulled from a list of styles in a SharePoint list, the Title of the podcast and finally a short description of the audience you want to present to.
 
### Source Content Screen
This is where the user will select what source they want to created the podcast from, this could be an upload of a PDF or Image, or they can simply copy/paste or write their own content.
 
### Podcast from Text Screen
If the user selects to copy/paster or type their own content in, they provide the content and then hit the “Script it!” button. This will fire off a workflow that will use all the inputs from the “Welcome Screen” to build a podcast script and present it in in SSML format (that they can edit) in the second text box.
After checking and modifying the SSML if needed, they then will the select the “Podcast it!” button, this will fire off a workflow that will take the SSML content and put it into an Azure Blob Storage Queue called “podcast-start”
 
#### Associated Flow: Podcaster – Process SSML – Text
This Power Automate action takes various pieces of input text from a trigger, maps them to parameters expected by the AI Builder custom prediction model, and then calls the model to generate predictions or insights based on the provided data. This is particularly useful for automating tasks such as generating podcast scripts from structured input data.
 
### Upload Screen
This where the user can upload a PDF or Image that will be sent to a flow for processing, output of which will be SSML in the text box they can edit before sending it generate audio.
 
#### Associated Flow: Podcaster – Process SSML from Upoad
Executed when user selects “Script it!” button. This flow processes a file's content that has been passed from the Power App, recognizes text from it, generates a custom podcast script in SMML using that text with AI Builder, and then creates an item in SharePoint with the generated SSML and the original recognized text.
 
#### Associated Flow: Podcaster – Generate Audio
Executed from when the user selects “Podcast it!” button. 

### Progress Screen
Presented to user after selecting “Podcast it!” button to explain that podcast audio is in process of being created which is being done by the Podcaster – Process Queue flow.

#### Associated Flow: Podcaster – Process Queue
Executed from when user select “Podcast it!” button. This flow processes messages from a queue, retrieves content from a blob storage, creates a file in SharePoint, and updates its properties with metadata such as title and description.

![image](https://github.com/user-attachments/assets/0a79d144-1498-4b37-9e7c-bfffb719e17a)

 
### Podcasts Screen
Allows the users to view and play recent podcasts pulled from a SharePoint list / to download a podcast.

## Power Automate Flows

## Power Automate Connectors

## SharePoint Components

 

