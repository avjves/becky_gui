import React from "react";
import Button from "@material-ui/core/Button";
import SettingsTableItem from './SettingsTableItem.js';

class SettingsTable extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            fs_root: '',
            temp: '',
        }
    }

    updateValue() {

    }

    render() {
        return (
            <div>
                <div>
                    <SettingsTableItem title="File selector root path" key="fs_root" settings={this.props.settings} updateValue={this.updateValue} />
                    <SettingsTableItem title="Second setting" key="temp" settings={this.props.settings} updateValue={this.updateValue} />
                </div>
                <div>
                    <Button variant='contained' className="m-1" color='primary' onClick={this.props.saveSettings}> Save settings</Button>
                </div>
            </div>
        )
    }

}

export default SettingsTable;
