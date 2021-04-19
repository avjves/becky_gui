import React from "react";
import { Button } from 'react-bootstrap';
import axios from 'axios';

import history from '../history.js';
import FileSelectorTreeView from '../objects/FileSelectorTreeView.js';
import TextField from '@material-ui/core/TextField';
import Header from '../objects/Header.js';

class SingleBackupRestoreView extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            restorePath: '',
            restoreSelections: {}
        }
        this.handleChangeRestorePath = this.handleChangeRestorePath.bind(this);
        this.fetchRestoreFilesByPath = this.fetchRestoreFilesByPath.bind(this);
        this.addFileSelection = this.addFileSelection.bind(this);
    }

    async fetchRestoreFilesByPath(path) {
        return axios.get("http://localhost:8000/backups/restore/files/" + this.props.backupId, {
            params: {
                path: path,
            }
        })

    }

    addFileSelection() {

    }

    handleChangeRestorePath(event) {
        this.setState({restorePath: event.target.value});
    }

    render() {
        return (
            <div>
                <Header text="Restore files:" />
                <hr />
                <FileSelectorTreeView fetchFilesByPath={this.fetchRestoreFilesByPath} addFileSelection={this.addFileSelection} />
                <div className="col-11">
                    <form>
                        <TextField style={{'width': '100%'}} id="restore_path" label="Restore path:" onChange={this.handleChangeRestorePath} />                
                    </form>
                </div>
            </div>
        );
    }
}

export default SingleBackupRestoreView;
