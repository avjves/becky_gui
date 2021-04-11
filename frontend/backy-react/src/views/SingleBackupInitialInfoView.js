import React from "react";
import { Form } from 'react-bootstrap';
import Button from "@material-ui/core/Button";
import { BrowserRouter as Router, Switch, Route, Link } from "react-router-dom";


class SingleBackupInitialInfoView extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            name: null,
            running: null,
        }

        this.onClickNextButton = this.onClickNextButton.bind(this);
    }


    onClickNextButton() {
        this.props.updateBackup(this.state);
    }

    
    render() {
        console.log(this.props)
        var defaultValues = {
            'name': this.props.backup.name ? this.props.backup.name : '',
            'running': this.props.backup.running ? 1 : 0,
        }
        return (
            <div>
                <Form>
                    <Form.Group controlId="formName">
                        <Form.Label> Backup name: </Form.Label>
                        <Form.Control type="username" placeholder="Enter backup name" defaultValue={defaultValues.name} onChange={e =>  this.setState({name: e.target.value})}/> 
                    </Form.Group>
                    <Form.Group controlId="formRunning">
                        <Form.Label> Running: </Form.Label>
                        <Form.Control type="text" placeholder="Enter 0 or 1" defaultValue={defaultValues.running} onChange={e => this.setState({running: e.target.value})}/> 
                    </Form.Group>
                    <Button variant="contained" color='primary' type="button" onClick={this.onClickNextButton}>
                        Next
                    </Button>
                </Form>

            </div>
        );
    }
}

export default SingleBackupInitialInfoView;
