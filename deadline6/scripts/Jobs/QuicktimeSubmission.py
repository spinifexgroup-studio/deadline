import clr
import sys

from System.IO import *

from Deadline.Scripting import *

from DeadlineUI.Controls.Scripting.DeadlineScriptDialog import DeadlineScriptDialog

scriptDialog = None
scriptPath = None

def __main__():
    global scriptDialog
    global scriptPath
    
    scriptDialog = DeadlineScriptDialog()
    scriptDialog.SetIcon( Path.Combine( RepositoryUtils.GetRootDirectory(), "plugins/Quicktime/Quicktime.ico" ) )
    
    selectedJobs = MonitorUtils.GetSelectedJobs()
    if len(selectedJobs) > 1:
        scriptDialog.ShowMessageBox( "Only one job can be selected at a time.", "Multiple Jobs Selected" )
        return
    
    scriptPath = Path.Combine( RepositoryUtils.GetScriptsDirectory(), "Submission/QuicktimeSubmission.py" )
    scriptPath = PathUtils.ToPlatformIndependentPath( scriptPath )
    
    outputFilenameCount = JobUtils.GetOutputFilenameCount( 0 )
    
    versionId = ""
    if outputFilenameCount > 0:
        job = selectedJobs[0]
        
        versionId = job.GetJobExtraInfoKeyValue( "VersionId" )
        if versionId != "":
            lines = []
            lines.append( "VersionId=%s" % versionId )
            
            if job.GetJobExtraInfoKeyValue( "EntityId" ) != "":
                lines.append( "EntityId=%s" % job.GetJobExtraInfoKeyValue( "EntityId" ) )
            if job.GetJobExtraInfoKeyValue( "EntityType" ) != "":
                lines.append( "EntityType=%s" % job.GetJobExtraInfoKeyValue( "EntityType" ) )
            if job.GetJobExtraInfoKeyValue( "ProjectId" ) != "":
                lines.append( "ProjectId=%s" % job.GetJobExtraInfoKeyValue( "ProjectId" ) )
            if job.GetJobExtraInfoKeyValue( "TaskId" ) != "":
                lines.append( "TaskId=%s" % job.GetJobExtraInfoKeyValue( "TaskId" ) )
                
            if job.JobExtraInfo0 != "":
                lines.append( "TaskName=%s" % job.JobExtraInfo0 )
            elif job.GetJobExtraInfoKeyValue( "TaskName" ) != "":
                lines.append( "TaskName=%s" % job.GetJobExtraInfoKeyValue( "TaskName" ) )
            
            if job.JobExtraInfo1 != "":
                lines.append( "ProjectName=%s" % job.JobExtraInfo1 )
            elif job.GetJobExtraInfoKeyValue( "ProjectName" ) != "":
                lines.append( "ProjectName=%s" % job.GetJobExtraInfoKeyValue( "ProjectName" ) )
            
            if job.JobExtraInfo2 != "":
                lines.append( "EntityName=%s" % job.JobExtraInfo2 )
            elif job.GetJobExtraInfoKeyValue( "EntityName" ) != "":
                lines.append( "EntityName=%s" % job.GetJobExtraInfoKeyValue( "EntityName" ) )
            
            if job.JobExtraInfo3 != "":
                lines.append( "VersionName=%s" % job.JobExtraInfo3 )
            elif job.GetJobExtraInfoKeyValue( "VersionName" ) != "":
                lines.append( "VersionName=%s" % job.GetJobExtraInfoKeyValue( "VersionName" ) )
            
            if job.JobExtraInfo4 != "":
                lines.append( "Description=%s" % job.JobExtraInfo4 )
            elif job.GetJobExtraInfoKeyValue( "Description" ) != "":
                lines.append( "Description=%s" % job.GetJobExtraInfoKeyValue( "Description" ) )
                
            if job.JobExtraInfo5 != "":
                lines.append( "UserName=%s" % job.JobExtraInfo5 )
            elif job.GetJobExtraInfoKeyValue( "UserName" ) != "":
                lines.append( "UserName=%s" % job.GetJobExtraInfoKeyValue( "UserName" ) )
            
            shotgunSettingsPath = Path.Combine( GetDeadlineSettingsPath(), "QuicktimeSettingsShotgun.ini" )
            File.WriteAllLines( shotgunSettingsPath, tuple(lines) )
    
    
    if outputFilenameCount > 1:
        dialogWidth = 600
        
        scriptDialog.SetSize( dialogWidth, (outputFilenameCount * 32) + 100 )
        scriptDialog.SetTitle( "Submit Quicktime Job To Deadline" )
        
        scriptDialog.AddControl( "Label", "LabelControl", "Please select the output images to create Quicktimes for.", dialogWidth - 16, -1 )
        for i in range( 0, outputFilenameCount ):
            outputFilename = JobUtils.GetOutputFilename( 0, i )
            outputFilename = RepositoryUtils.CheckPathMapping( outputFilename, False )
            outputFilename = PathUtils.ToPlatformIndependentPath( outputFilename )
            scriptDialog.AddSelectionControl( str(i), "CheckBoxControl", (i==0), Path.GetFileName( outputFilename ), dialogWidth - 16, -1 )
        
        scriptDialog.AddRow()
        scriptDialog.AddControl( "DummyLabel1", "LabelControl", "", dialogWidth - 232, -1 )
        submitButton = scriptDialog.AddControl( "SubmitButton", "ButtonControl", "Submit", 100, -1 )
        submitButton.ValueModified.connect(SubmitButtonPressed)
        closeButton = scriptDialog.AddControl( "CloseButton", "ButtonControl", "Close", 100, -1 )
        closeButton.ValueModified.connect(CloseButtonPressed)
        scriptDialog.EndRow()
        
        scriptDialog.ShowDialog( True )
    else:
        outputFilename = JobUtils.GetFirstOutputFilename( 0 )
        outputFilename = RepositoryUtils.CheckPathMapping( outputFilename, False )
        outputFilename = PathUtils.ToPlatformIndependentPath( outputFilename )
        
        arguments = (outputFilename,)
        if versionId != "":
            arguments = (outputFilename, "EnableShotgun")
        
        ClientUtils.ExecuteScript( scriptPath, arguments )

def CloseDialog():
    global scriptDialog
    scriptDialog.CloseDialog()

def CloseButtonPressed(*args):
    CloseDialog()
    
def SubmitButtonPressed(*args):
    global scriptDialog
    global scriptPath
    
    selectedJobs = MonitorUtils.GetSelectedJobs()
    job = selectedJobs[0]
    
    versionId = job.GetJobExtraInfoKeyValue( "VersionId" )
    
    outputFilenameCount = JobUtils.GetOutputFilenameCount( 0 )
    for i in range( 0, outputFilenameCount ):
        if bool(scriptDialog.GetValue( str(i) ) ):
            outputFilename = JobUtils.GetOutputFilename( 0, i )
            outputFilename = RepositoryUtils.CheckPathMapping( outputFilename, False )
            outputFilename = PathUtils.ToPlatformIndependentPath( outputFilename )
            
            arguments = (outputFilename,)
            if versionId != "":
                arguments = (outputFilename, "EnableShotgun")
            
            ClientUtils.ExecuteScript( scriptPath, arguments )
    
    CloseDialog()
