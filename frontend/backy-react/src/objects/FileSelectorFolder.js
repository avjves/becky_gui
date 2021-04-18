import React from 'react';

import FileSelectorFile from './FileSelectorFile.js';

class FileSelectorFolder extends React.Component {

    render() {
        var folderAsFile = <FileSelectorFile file={this.props.file} toggleFile={this.props.toggleFile} addFileSelection={this.props.addFileSelection} status={this.props.status} fileType="directory" filename={this.props.filename} level={this.props.level} />

        if(this.props.file.open) {
            return (
                <div className="">
                    {folderAsFile}
                    <div>
                        {this.props.files.map((file, index) => {
                            return <div key={index}>{file}</div>
                        })}
                    </div>
                </div>
            );
        }
        else {
            return (
                <div>
                    {folderAsFile}
                </div>
            );

        }
    }
}


export default FileSelectorFolder;
