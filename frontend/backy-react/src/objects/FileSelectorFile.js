import React from 'react';
import { Form } from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faFolder, faFile, faChevronDown, faChevronRight } from '@fortawesome/free-solid-svg-icons';



class FileSelectorFile extends React.Component {

    constructor(props) {
        super(props);

        this.toggleFile = this.toggleFile.bind(this);
    }

    getFileIcon(fileType) {
        var icon = null;
        if(fileType == "directory") {
            icon = <FontAwesomeIcon icon={faFolder} />
        }
        else {
            icon = <FontAwesomeIcon icon={faFile} />
        }
        return icon;
    }

    getStatusIcon(fileType, open) {
        var icon = null;
        if(fileType == 'file' || open != true) {
            icon = <FontAwesomeIcon icon={faChevronRight} />
        }
        else {
            icon = <FontAwesomeIcon icon={faChevronDown} />
        }
        return icon;
    }

    toggleFile() {
        if(this.props.file.file_type == 'directory') {
            console.log(this.props.file);
            this.props.toggleFile(this.props.file.directory, this.props.file.filename);
        }
    }

    render() {
        var leftMargin = 25*this.props.level;
        var fileIcon = this.getFileIcon(this.props.fileType);
        var statusIcon = this.getStatusIcon(this.props.fileType, this.props.file.open);

        return (
            <div>
                <div style={{'marginLeft': leftMargin}} className="row">

                    <div className="col-1" onClick={this.toggleFile}>
                        {statusIcon}
                    </div>

                    <div className="col-1">
                        {fileIcon}
                    </div>


                    <div className="col-1">
                        <Form>
                            <Form.Group className="d-flex" controlId="formSelected">
                                <Form.Check type="checkbox"/>
                            </Form.Group>
                        </Form>
                    </div>


                    
                    <div className="col-9">
                        <span>{this.props.filename}</span>
                    </div>
                </div>
                <hr />
            </div>
        );
    }
}


export default FileSelectorFile;
