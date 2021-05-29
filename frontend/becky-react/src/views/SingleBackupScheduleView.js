import React from "react";
import Typography from "@material-ui/core/Typography";
import InputLabel from '@material-ui/core/InputLabel';
import FormHelperText from '@material-ui/core/FormHelperText';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';


class SingleBackupScheduleView extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            backup_schedule: this.props.backup.backup_schedule ? this.props.backup.backup_schedule : 'minute',
            retention_schedule: this.props.backup.retention_schedule ? this.props.backup.retention_schedule : '0',
        }

        this.onClickNextButton = this.onClickNextButton.bind(this);
    }


    onClickNextButton() {
        this.props.updateBackup(this.state);
    }

    
    render() {
        return (
            <div>
                <Typography variant="h6"> Backup schedule: </Typography>
                <hr />
                <Typography variant="h7"> Select when to run the backup: </Typography>
                <div>
                    <FormControl style={{'width': '100%'}}>
                            <InputLabel htmlFor="age-native-simple">Backup every:</InputLabel>
                                <Select native value={this.state.backup_schedule} defaultValue={this.state.backup_schedule} onChange={(e) => {this.setState({backup_schedule: e.target.value})}} inputProps={{name: 'backupSchedule'}}>
                                    <option aria-label="None" value="" />
                                    <option value={'minute'}>Minute</option>
                                    <option value={'hour'}>Hour</option>
                                    <option value={'day'}>Day</option>
                                </Select>
                    </FormControl>
                </div>
                <hr />
                <Typography variant="h7"> Select backup retention: </Typography>
                <FormControl style={{'width': '100%'}}>
                    <TextField id="retention_days" label="Number" type="number" defaultValue={this.state.retention_schedule} onChange={(e) => {this.setState({retention_schedule: e.target.value })}} />
                </FormControl>
                <hr />
                <Button variant="contained" color='primary' type="button" onClick={this.onClickNextButton}>
                    Next
                </Button>
            </div>);
    }
}

export default SingleBackupScheduleView;
