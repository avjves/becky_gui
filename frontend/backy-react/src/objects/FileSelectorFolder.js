import React from 'react';

import FileSelectorFile from './FileSelectorFile.js';

class FileSelectorFolder extends React.Component {

    render() {
        if(this.props.file.open) {
            return (
                <div className="">
                    <FileSelectorFile file={this.props.file} toggleFile={this.props.toggleFile} status={this.props.status} fileType="directory" filename={this.props.filename} level={this.props.level} />
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
                    <FileSelectorFile file={this.props.file} toggleFile={this.props.toggleFile} status={this.props.status} fileType="directory" filename={this.props.filename} level={this.props.level} />
                </div>
            );

        }
    }
}


export default FileSelectorFolder;
