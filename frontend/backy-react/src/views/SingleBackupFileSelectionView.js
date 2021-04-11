import React from "react";
import { Form } from 'react-bootstrap';
import Button from "@material-ui/core/Button";
import { BrowserRouter as Router, Switch, Route, Link } from "react-router-dom";


class SingleBackupFileSelectionView extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            path: null
        }

        this.onClickNextButton = this.onClickNextButton.bind(this);
    }


    onClickNextButton() {
        this.props.updateBackup(this.state);
    }

    
    render() {
        var defaultValues = {
            'path': this.props.backup.path ? this.props.backup.path : '',
        }
        return (
            <div>
                <Form>
                    <Form.Group controlId="formName">
                        <Form.Label> Path: </Form.Label>
                        <Form.Control type="text" placeholder="Enter filepath to be backupped" defaultValue={defaultValues.path} onChange={e =>  this.setState({path: e.target.value})}/> 
                    </Form.Group>
                    <Button variant="contained" color='primary' type="button" onClick={this.onClickNextButton}>
                        Next
                    </Button>
                </Form>
            </div>
        );
    }
}

export default SingleBackupFileSelectionView;
