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
    }

    componentDidMount() {
        this.updateFileTree('/');
    }

    async updateFileTree(path) {
        var files = await this.props.fetchFilesByPath(path);
        files = files.data.files;
        var currentFileTree = this.state.fileTree;
        //currentFileTree = this.addDirectory(currentFileTree, files[0].directory);
        for(var file of files) {
            var directory = file.directory;
            var currentFile = file.filename;
            var selected = file.selected;
            currentFileTree = this.addFile(currentFileTree, file);
        }
        this.setState({fileTree: currentFileTree});
    }

    addDirectory(fileTree, directoryToAdd) {
        if(directoryToAdd.length == 0) {
            return fileTree;
        }
        var folders = directoryToAdd.split("/");
        var steps = [];
        var cur = fileTree;
        for(var folder of folders) {
            if(folder in cur.files) {
                cur = cur.files[folder];
            }
            else {
                cur.files[folder] = {'fileType': 'directory', 'name': folder, 'files': {}, 'selected': false};
                cur = cur.files[folder];
            }
        }
        return fileTree;
    }

    addFile(fileTree, file) {
        var fileDirectory = this.getFileDirectory(fileTree, file.directory);
        console.log("Adding file", file);
        if(file.filename in fileDirectory.files) {
            //console.log("File " + file.filename + "already added to tree at " + file.directory);
        }
        else {
            //var newFile = {'fileType': 'file', 'name': fileToAdd, 'selected': isSelected};
            fileDirectory.files[file.filename] = file;
        }
        return fileTree;
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

    makeDirPath(directory, file) {
        if(directory.endsWith('/')) {
            return directory + file;
        }
        else {
            return directory + '/' + file;
        }
    }

    selectFile(event) {
        console.log("selected file", event.target.innerHTML)
    }

    toggleFile(directory, file) {
        console.log("Toggling file", file);
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

    getDirectoryFilesAsHTML(directory) {
        var files = [];
        for(var file in directory.files) {
            var fileData = directory.files[file];
            if(fileData.file_type == 'directory') {
                files.push(this.getDirectoryFilesAsHTML(fileData));
            }
            else {
                files.push(<FileSelectorFile file={fileData} path={fileData.path} fileType="file" filename={fileData.filename} selectFile={this.selectFile} level={directory.level+1}/>);
            }
        }
        return <FileSelectorFolder file={directory} toggleFile={this.toggleFile} fileType="directory" filename={directory.filename} files={files} status={directory.status} level={directory.level}/>

    }

    render() {
        var treeElements = this.getDirectoryFilesAsHTML(this.state.fileTree);
        console.log(this.state.fileTree);
        return (
            <div style={{'height': '200px', 'height': '500px', 'overflow': 'auto'}} className="m-2 p-1 border">
                {treeElements} 
            </div>
        );
    }

}
export default FileSelectorTreeView;
