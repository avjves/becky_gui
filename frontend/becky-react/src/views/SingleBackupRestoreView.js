import React from "react";
import axios from 'axios';

import history from '../history.js';
import FileSelectorTreeView from '../objects/FileSelectorTreeView.js';
import TextField from '@material-ui/core/TextField';
import Button from '@material-ui/core/Button';
import Header from '../objects/Header.js';

class SingleBackupRestoreView extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            restorePath: '',
            restoreSelections: {}
        }
        this.onChangeRestorePath = this.onChangeRestorePath.bind(this);
        this.fetchRestoreFilesByPath = this.fetchRestoreFilesByPath.bind(this);
        this.addFileSelection = this.addFileSelection.bind(this);
        this.onClickNextButton = this.onClickNextButton.bind(this);
    }

    async fetchRestoreFilesByPath(path) {
        return axios.get("http://localhost:8000/backups/restore/files/" + this.props.backupId, {
            params: {
                path: path,
            }
        })

    }

    addFileSelection(selection) {
        var currentSelections = this.state.restoreSelections;
        if(selection in currentSelections) {
            console.log("Deleting a file selection", selection);
            delete currentSelections[selection] 
        }
        else {
            console.log("Adding a file selection", selection);
            currentSelections[selection] = true;
        }
        this.setState({restoreSelections: currentSelections});

    }

    onChangeRestorePath(event) {
        this.setState({restorePath: event.target.value});
    }


    onClickNextButton(event) {
        this.startRestoration();
    }

    startRestoration() {
        return axios.post("http://localhost:8000/backups/restore/" + this.props.backupId + "/", {
            selections: this.state.restoreSelections,
            restore_path: this.state.restorePath,
        })
        .then((data) => {
            console.log(data)
            history.push('/backups/list');
        })
    }


    render() {
        return (
            <div>
                <Header text="Restore files:" />
                <hr />
                <FileSelectorTreeView fetchFilesByPath={this.fetchRestoreFilesByPath} addFileSelection={this.addFileSelection} />
                <div className="col-11">
                    <form>
                        <TextField style={{'width': '100%'}} id="restore_path" label="Restore path:" onChange={this.onChangeRestorePath} />                
                    </form>
                </div>
                <hr />
                <div className="row justify-content-end mr-5 mb-2">
                    <Button variant="contained" color='primary' type="button" onClick={this.onClickNextButton}>
                        Next
                    </Button>
                </div>
            </div>
        );
    }
}

export default SingleBackupRestoreView;
