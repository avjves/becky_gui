import React from "react";
import Button from "@material-ui/core/Button";
import { Link, Menu } from "react-router-dom";

class BackupListObject extends React.Component {
    constructor(props) {
        super(props);
        this.run = this.run.bind(this);
    }

    run() {
        fetch('http://localhost:8000/backups/run/' + this.props.backup.id + "/", {
            method: 'GET',
            credentials: "include",
        });
    }

    render() {
        console.log(this.props.backup)
        return (
            <div className="row">
                <div className="col-10 mt-auto mb-auto">
                    <div>
                        <span>Name: {this.props.backup.name}</span><br />
                    </div>
                    <span>Provider: {this.props.backup.provider}</span><br />
                    <span>Path: {this.props.backup.path}</span><br />
                </div>
                <div className="col-2 mt-1">
                    <Button variant='contained' className="m-1" color='primary' component={Link} to={"/backups/edit/" + this.props.backup.id + "/0"}> Edit </Button>
                    <Button variant='contained' className="m-1" color='primary' onClick={this.run}> run </Button>
                    <Button variant='contained' className="m-1" color='primary' component={Link} to={"/backups/logs/" + this.props.backup.id}>Show logs</Button>
                </div>

            </div>
        );
    }
}

export default BackupListObject;
