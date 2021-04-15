import React from 'react';

class FileSelectorTreeView extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            fileTree: {'fileType': 'directory', 'name': '/', 'files': {}}
        }
        this.updateFileTree = this.updateFileTree.bind(this);
    }

    componentDidMount() {
        this.updateFileTree('/');
    }

    async updateFileTree(path) {
        var files = await this.props.fetchFilesByPath(path);
        files = files.data.files;
        console.log("files", files);
        var currentFileTree = this.state.fileTree;
        currentFileTree = this.addDirectory(currentFileTree, files[0].directory);
        for(var file of files) {
            console.log("going through file", file);
            var directory = file.directory;
            var currentFile = file.filename;
            var selected = file.selected;
            //console.log("FT before", JSON.stringify(currentFileTree))
            //console.log("FT after dict", currentFileTree)
            currentFileTree = this.addFile(currentFileTree, file);
            //console.log("FT after file", JSON.stringify(currentFileTree))
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
            console.log("going throug folder", folder)
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
        if(file.filename in fileDirectory.files) {
            console.log("File " + file.filename + "already added to tree at " + file.directory);
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
        for(var folder of directory) {
            cur = cur.files[folder];
        }
        return cur;
    }


    getFileTreeAsHTMLElements() {
        var elements = [];
        console.log(this.state.fileTree);
    }

    render() {
        var elements = this.getFileTreeAsHTMLElements();        
        return (
            ''
        );
    }

}
export default FileSelectorTreeView;
