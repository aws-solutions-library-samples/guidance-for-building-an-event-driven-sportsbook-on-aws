import { Typography, Card, IconButton } from "@mui/material";
import DeleteIcon from '@mui/icons-material/Delete';
import { useSystemEvents, useClearHistory } from "../../hooks/useSystemEvents";
import { DataGrid } from "@mui/x-data-grid";

export const SystemEvents = () => {
    const {data: systemEvents, isLoading: loadingSystemEvents } = useSystemEvents();
    const { mutateAsync: clearHistory } = useClearHistory();
    if(loadingSystemEvents) return <Typography>Loading...</Typography>

    const columns = [
        {
            field: 'id',
            headerName: 'ID',
            sortable: true,
            flex: 0.1,
        },
        {
            field: 'source',
            headerName: 'source',
            sortable: true,
            flex: 0.4,
            renderCell: ({row}) => {
                <Typography>{row.source}</Typography>
            }
        },
        {
            field: 'detailType',
            headerName: 'detailType',
            sortable: true,
            flex: 0.4,
            renderCell: ({row}) => {
                <Typography>{row.detailType}</Typography>
            }
        },
        {
            field: 'detail',
            headerName: 'detail',
            sortable: true,
            flex: 1.5,
            renderCell: ({row}) => {
                <Typography>{row.detail}</Typography>
            }
        }
    ]

    return (
        <Card>
          <IconButton 
            color="error"
            size="small"
            onClick={clearHistory}>
              Clear
              <DeleteIcon />
          </IconButton>
            <DataGrid
                rows={systemEvents}
                rowHeight={25}
                columns={columns}
                pageSizeOptions={[10]}
                initialState={{
                    pagination: {
                      paginationModel: {
                        pageSize: 10,
                      },
                    },
                    sorting: {
                        sortModel: [{field: 'id', sort: 'desc'}]
                    }
                  }}
            />
        </Card>
    )
}

export default SystemEvents;