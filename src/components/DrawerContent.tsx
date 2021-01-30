import { List } from '@material-ui/core';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import HomeIcon from '@material-ui/icons/Home';
import TableChartIcon from '@material-ui/icons/TableChart';
import { observer } from 'mobx-react';
import { default as React, FunctionComponent } from 'react';

export const DrawerContent: FunctionComponent = observer(() => {
    return (
        <List>
            <ListItem button key="Home">
                <ListItemIcon>
                    <HomeIcon />
                </ListItemIcon>
                <ListItemText primary="Home" />
            </ListItem>
            <ListItem button key="Caseload">
                <ListItemIcon>
                    <TableChartIcon />
                </ListItemIcon>
                <ListItemText primary="Caseload" />
            </ListItem>
        </List>
    );
});

export default DrawerContent;
