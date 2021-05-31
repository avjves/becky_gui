import React from "react";
import axios from 'axios';

import history from '../history.js';
import FileSelectorTreeView from '../objects/FileSelectorTreeView.js';
import TextField from '@material-ui/core/TextField';
import FormControl from '@material-ui/core/FormControl';
import InputLabel from '@material-ui/core/InputLabel';
import Select from '@material-ui/core/Select';
import Button from '@material-ui/core/Button';
import Header from '../objects/Header.js';

class SingleBackupRestoreView extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            restorePath: '',
            restoreSelections: {},
            currentIterationTimestamp: 0,
            readyToRender: false,
            timestamps: [],
        }
        this.onChangeRestorePath = this.onChangeRestorePath.bind(this);
        this.fetchRestoreFilesByPath = this.fetchRestoreFilesByPath.bind(this);
        this.addFileSelection = this.addFileSelection.bind(this);
        this.onClickNextButton = this.onClickNextButton.bind(this);
        this.onChangeIteration = this.onChangeIteration.bind(this);
    }

    async fetchRestoreFilesByPath(path) {
        return axios.get("http://localhost:6701/api/backups/restore/files/" + this.props.backupId, {
            params: {
                path: path,
                backup_timestamp: this.state.currentIterationTimestamp,
            }
        })

    }

    fetchBackupIterations() {
        fetch("http://localhost:6701/api/backups/backup/" + this.props.backupId, {
            method: 'GET',
            credentials: "include",
        })
        .then((res) => res.json())
        .then((data) => {
            console.log(data.backup.timestamps)
            var timestamps = data.backup.timestamps;
            this.setState({timestamps: timestamps, currentIterationTimestamp: timestamps[timestamps.length-1], readyToRender: true});
        })
        .catch((err) => {
            console.log("ERROR", err);
        });
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

    onChangeIteration(event) {
        this.setState({currentIterationTimestamp: event.target.value, readyToRender: false}, (e) => this.setState({readyToRender: true})); // Force the tree view to rerender!
    }

    onClickNextButton(event) {
        this.startRestoration();
    }

    componentDidMount() {
        this.fetchBackupIterations();
    }

    startRestoration() {
        return axios.post("http://localhost:6701/api/backups/restore/" + this.props.backupId + "/", {
            selections: this.state.restoreSelections,
            restore_path: this.state.restorePath,
            backup_timestamp: this.state.currentIterationTimestamp,
        })
        .then((data) => {
            console.log(data)
            history.push('/backups/list');
        })
    }

    timestampsAsHTML(timestamps) {
        var html_objects = [];
        for(var i = 0; i < timestamps.length; i++) {
            var unix = timestamps[i];
            var uiUnix = unix.split(".")[0]; // Lose last few ms
            var date = new Date(uiUnix*1000);
            var formattedTime = date.getHours() + ':' + date.getMinutes() + ':' + date.getSeconds();

            html_objects.push(<option key={i} value={unix}>{formattedTime}</option>);
        }
        return html_objects;
    }


    render() {
        console.log(this.state.currentIterationTimestamp);
        var fileSelector = '';
        if(this.state.readyToRender) {
            var fileSelector = <FileSelectorTreeView fetchFilesByPath={this.fetchRestoreFilesByPath} addFileSelection={this.addFileSelection} />
        }
        var timestamps = this.timestampsAsHTML(this.state.timestamps);
        return (
            <div>
                <Header text="Restore files:" />
                <Header size="h3" text="Choose backup iteration:" />
                <FormControl style={{'width': '100%'}}>
                            <InputLabel htmlFor="age-native-simple">Date:</InputLabel>
                            <Select native value={this.state.currentIterationTimestamp} onChange={this.onChangeIteration} inputProps={{name: 'iteration'}}>
                                {timestamps}
                            </Select>
                </FormControl>

                <hr />
                {fileSelector}
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
