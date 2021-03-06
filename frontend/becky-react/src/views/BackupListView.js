import React from "react";
import Button from "@material-ui/core/Button";
import { BrowserRouter as Router, Switch, Route, Link, UseRouteMatch, useParams } from "react-router-dom";

import BackupListObject from '../objects/BackupListObject.js';
import Header from '../objects/Header.js';

class BackupListView extends React.Component {

    constructor(props) {
        super(props);
    }

    
    render() {
        return (
        <div>
            <Header size="h2">All backups: </Header>
                {this.props.backups.map((backup, index) => {
                    return (
                        <div key={index} className="card m-2">
                            <BackupListObject backup={backup} deleteBackup={this.props.deleteBackup}/>
                        </div>
                    )
                })}
            <Button variant='contained' color='primary' type="button">
                <Link style={{'color': 'white'}} to={"/backups/edit/-1/0"}>Add a new backup </Link>
            </Button>
        </div>
        );
    }
}

export default BackupListView;
