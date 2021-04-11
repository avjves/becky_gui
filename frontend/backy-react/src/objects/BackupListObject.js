import React from "react";
import Button from "@material-ui/core/Button";
import { Link, Menu } from "react-router-dom";

class BackupListObject extends React.Component {
    constructor(props) {
        super(props);
    }


    render() {
        console.log(this.props.backup)
        return (
            <div className="row">
                <div className="mt-3 mr-2 ml-1 col-1">
                    <Button variant='contained' color='primary' component={Link} to={"/backups/" + this.props.backup.id + "/0"}> Edit </Button>
                </div>
                <div className="col-8">
                    <div>
                        <span>Name: {this.props.backup.name}</span><br />
                    </div>
                    <span>Provider: {this.props.backup.provider}</span><br />
                    <span>Running: {this.props.backup.running ? 'YES' : 'NO'}</span><br />
                </div>
            </div>
        );
    }
}

export default BackupListObject;
