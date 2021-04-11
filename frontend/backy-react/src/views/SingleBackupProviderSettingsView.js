import React from "react";
import { Form } from 'react-bootstrap';
import Button from "@material-ui/core/Button";
import { BrowserRouter as Router, Switch, Route, Link } from "react-router-dom";


class SingleBackupProviderSettingsView extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            provider: null,
            providerSettings: null,
        }

        this.onClickNextButton = this.onClickNextButton.bind(this);
    }


    onClickNextButton() {
        this.props.updateBackup(this.state);
    }

    
    render() {
        var defaultValues = {
            'provider': this.props.backup.provider ? this.props.backup.provider : '',
            'providerSettings': this.props.backup.providerSettings ? this.props.backup.providerSettings : '',
        }
        return (
            <div>
                <Form>
                    <Form.Group controlId="formName">
                        <Form.Label> Provider name: </Form.Label>
                        <Form.Control type="username" placeholder="Enter provider name" defaultValue={defaultValues.provider} onChange={e =>  this.setState({provider: e.target.value})}/> 
                    </Form.Group>
                    <Form.Group controlId="formRunning">
                        <Form.Label> Provider settings: </Form.Label>
                        <Form.Control type="text" placeholder="Enter provider settings as JSON" defaultValue={defaultValues.providerSettings} onChange={e => this.setState({providerSettings: e.target.value})}/> 
                    </Form.Group>
                    <Button variant="contained" color='primary' type="button" onClick={this.onClickNextButton}>
                        Next
                    </Button>
                </Form>

            </div>
        );
    }
}

export default SingleBackupProviderSettingsView;
