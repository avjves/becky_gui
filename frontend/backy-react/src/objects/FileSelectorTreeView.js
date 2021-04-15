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
        return (
            <div style={{'height': '200px', 'height': '500px', 'overflowX': 'auto', 'whiteSpace': 'nowrap'}} className="m-2 p-1 border">
                {treeElements} 
            </div>
        );
    }

}
export default FileSelectorTreeView;
