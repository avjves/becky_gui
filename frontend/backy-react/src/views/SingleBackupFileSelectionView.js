import React from "react";
import { Form } from 'react-bootstrap';
import Button from "@material-ui/core/Button";
import axios from 'axios';
import FileSelectorTreeView from '../objects/FileSelectorTreeView.js';


class SingleBackupFileSelectionView extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            selections: {}
        }
        this.onClickNextButton = this.onClickNextButton.bind(this);
        this.fetchFilesByPath = this.fetchFilesByPath.bind(this);
        this.addFileSelection = this.addFileSelection.bind(this);
    }


    onClickNextButton() {
        this.props.updateBackup(this.state);
    }

    addFileSelection(filePath, selected) {
        var currentSelections = this.state.selections; 
        currentSelections[filePath] = selected;
        this.setState({selections: currentSelections});
    }

    async fetchFilesByPath(path) {
        return axios.get("http://localhost:8000/backups/files/" + this.props.backup.id, {
            params: {
                path: path,
            }
        })
    }
    
    render() {
        var defaultValues = {
            'path': this.props.backup.path ? this.props.backup.path : '',
        }
        return (
            <div>
                <FileSelectorTreeView fetchFilesByPath={this.fetchFilesByPath} addFileSelection={this.addFileSelection}/>
                <Button variant="contained" color='primary' type="button" onClick={this.onClickNextButton}>
                    Next
                </Button>
            </div>
        );
    }
}

export default SingleBackupFileSelectionView;
