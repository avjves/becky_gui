import React from "react";
import Button from "@material-ui/core/Button";
import SettingsTableItem from './SettingsTableItem.js';

class SettingsTable extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
        }
        this.updateValue = this.updateValue.bind(this);
    }

    updateValue(key, value) {
        this.setState({[key]: value});
    }


    render() {
        return (
            <div>
                <div>
                    <SettingsTableItem title="File selector root path" settingKey="fs_root" value={this.props.settings.fs_root} updateValue={this.updateValue} />
                    <SettingsTableItem title="Second setting" settingKey="test_setting" value={this.props.settings.test_setting} updateValue={this.updateValue} />
                </div>
                <div>
                    <Button variant='contained' className="m-1" color='primary' onClick={(e) => this.props.saveSettings(this.state)}> Save settings</Button>
                </div>
            </div>
        )
    }

}

export default SettingsTable;
