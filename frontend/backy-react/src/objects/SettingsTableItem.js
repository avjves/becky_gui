import React from "react";
import { Form } from "react-bootstrap";

class SettingsTableItem extends React.Component {

    constructor(props) {
        super(props);
    }

    render() {
        var defaultValue = this.props.value ? this.props.value : '';
        return (
            <div>
                <Form>
                    <Form.Group controlId="settingName">
                        <Form.Label> {this.props.title}: </Form.Label>
                        <Form.Control type="text" placeholder="Enter setting value" defaultValue={defaultValue} onChange={(e) =>  this.props.updateValue(this.props.settingKey, e.target.value)}/> 
                    </Form.Group>
                </Form>
            </div>
        )
    }


}

export default SettingsTableItem;
