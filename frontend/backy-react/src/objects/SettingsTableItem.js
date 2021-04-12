import React from "react";
import { Form } from "react-bootstrap";

class SettingsTableItem extends React.Component {

    constructor(props) {
        super(props);
        this.state = {

        }
    }

    render() {
        var setting = this.props.setting;
        var defaultValue = '';
        return (
            <div>
                <Form>
                    <Form.Group controlId="settingName">
                        <Form.Label> {this.props.title}: </Form.Label>
                        <Form.Control type="text" placeholder="Enter setting value" defaultValue={defaultValue} param={this.props.key} onChange={e =>  this.props.updateValue}/> 
                    </Form.Group>
                </Form>
            </div>
        )
    }


}

export default SettingsTableItem;
