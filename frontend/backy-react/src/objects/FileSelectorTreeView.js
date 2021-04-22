import React from 'react';

import FileSelectorFile from '../objects/FileSelectorFile.js';
import FileSelectorFolder from '../objects/FileSelectorFolder.js';

class FileSelectorTreeView extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            fileTree: {'file_type': 'directory', 'directory': '', 'filename': '/', 'files': {}, 'open': true, 'level': 0}
        }
        this.updateFileTree = this.updateFileTree.bind(this);
        this.toggleFile = this.toggleFile.bind(this);
        this.getDirectoryFilesAsHTML = this.getDirectoryFilesAsHTML.bind(this);
        this.addFileSelection = this.addFileSelection.bind(this);
    }

    componentDidMount() {
        this.updateFileTree('/');
    }

    async updateFileTree(path) {
        var files = await this.props.fetchFilesByPath(path);
        files = files.data.files;
        var currentFileTree = this.state.fileTree;
        for(var file of files) {
            var directory = file.directory;
            var currentFile = file.filename;
            var selected = file.selected;
            currentFileTree = this.addFile(currentFileTree, file);
        }
        this.setState({fileTree: currentFileTree});
    }

    addFile(fileTree, file) {
        var fileDirectory = this.getFileDirectory(fileTree, file.directory);
        if(!(file.filename in fileDirectory.files)) {
            console.log("Adding", file)
            fileDirectory.files[file.filename] = file;
        }
        return fileTree;
    }

    addFileSelection(path, checked) {
        console.log(path);
        var currentFileTree = this.state.fileTree;
        var selectedFile = this.getFile(currentFileTree, path);    
        selectedFile.selected = !selectedFile.selected;
        this.setState({fileTree: currentFileTree});
        this.props.addFileSelection(path, checked);
    }

    getFileDirectory(fileTree, directory) {
        var folders = directory.split("/");
        var cur = fileTree;
        for(var folder of folders) {
            if(folder) {
                cur = cur.files[folder];
            }
        }
        return cur;
    }

    getFile(fileTree, filePath) {
        return this.getFileDirectory(fileTree, filePath);
    }

    makeDirPath(directory, file) {
        if(directory.endsWith('/')) {
            return directory + file;
        }
        else {
            return directory + '/' + file;
        }
    }

    toggleFile(directory, file) {
        var currentFileTree = this.state.fileTree;
        var fileDirectory = this.getFileDirectory(currentFileTree, this.makeDirPath(directory, file));
        if(fileDirectory.open) {
            fileDirectory.open = false;    
            this.setState({fileTree: currentFileTree});
        }
        else {
            fileDirectory.open = true;
            this.setState({fileTree: currentFileTree});
            this.updateFileTree(this.makeDirPath(directory, file));
        }
    }

    getImplicitFolders(directory) {
        var folders = [];
        for(var file in directory.files) {
            console.log("Going through", file)
            var fileData = directory.files[file];
            if(fileData.selected) {
                folders.push(fileData.directory);
            }
            if(fileData.file_type == 'directory') {
                var new_folders = this.getImplicitFolders(fileData);
                folders = folders.concat(new_folders);
            }
        }
        return folders;
    }

    getDirectoryFilesAsHTML(directory, implicitSelection) {
        var files = [];
        for(var file in directory.files) {
            var fileData = directory.files[file];
            var propagateImplicitSelection = null;
            if(directory.selected || implicitSelection) {
                propagateImplicitSelection = true;
            }
            else {
                propagateImplicitSelection = false;
            }
            if(fileData.file_type == 'directory') {
                files.push(this.getDirectoryFilesAsHTML(fileData, propagateImplicitSelection));
            }
            else {
                files.push(<FileSelectorFile file={fileData} implicitSelection={propagateImplicitSelection} path={fileData.path} addFileSelection={this.addFileSelection} fileType="file" filename={fileData.filename} selectFile={this.selectFile} level={directory.level+1}/>);
            }
        }
        return <FileSelectorFolder file={directory} toggleFile={this.toggleFile} implicitSelection={implicitSelection} addFileSelection={this.addFileSelection} fileType="directory" filename={directory.filename} files={files} status={directory.status} level={directory.level}/>

    }

    render() {
        //var implicitFolders = this.getImplicitFolders(this.state.fileTree);
        var treeElements = this.getDirectoryFilesAsHTML(this.state.fileTree, false);
        return (
            <div style={{'height': '200px', 'height': '500px', 'overflowX': 'auto', 'whiteSpace': 'nowrap'}} className="m-2 p-1 border">
                {treeElements} 
            </div>
        );
    }

}
export default FileSelectorTreeView;
