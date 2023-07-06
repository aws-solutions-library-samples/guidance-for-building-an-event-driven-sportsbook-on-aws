import { Typography, Card, Button, Box, ButtonGroup } from "@mui/material";
import { useSystemEvents } from "../../hooks/useSystemEvents";
import { DataGrid } from "@mui/x-data-grid";

export const SystemEvents = () => {
    const {data: systemEvents, isLoading: loadingSystemEvents} = useSystemEvents();
    if(loadingSystemEvents) return <Typography>Loading...</Typography>

    const columns = [
        {
            field: 'source',
            headerName: 'source',
            sortable: true,
            flex: 1,
            renderCell: ({row}) => {
                <Typography>{row.source}</Typography>
            }
        },
        {
            field: 'detailType',
            headerName: 'detailType',
            sortable: true,
            flex: 1,
            renderCell: ({row}) => {
                <Typography>{row.detailType}</Typography>
            }
        },
        {
            field: 'detail',
            headerName: 'detail',
            sortable: true,
            flex: 1,
            renderCell: ({row}) => {
                <Typography>{row.detail}</Typography>
            }
        }
    ]

    return (
        <Card>
            <DataGrid
                rows={systemEvents}
                columns={columns}
                pageSizeOptions={[10]}
            />
        </Card>
    )
}

export default SystemEvents;