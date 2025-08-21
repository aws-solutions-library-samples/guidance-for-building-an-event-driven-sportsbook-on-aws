import { Typography, Card, IconButton, Box, useTheme, useMediaQuery } from "@mui/material";
import DeleteIcon from '@mui/icons-material/Delete';
import { useSystemEvents, useClearHistory } from "../../hooks/useSystemEvents";
import { DataGrid } from "@mui/x-data-grid";

export const SystemEventsTable = () => {
    const {data: systemEvents, isLoading: loadingSystemEvents } = useSystemEvents();
    const { mutateAsync: clearHistory } = useClearHistory();
    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
    const isTablet = useMediaQuery(theme.breakpoints.down('md'));
    
    if(loadingSystemEvents) return <Typography>Loading...</Typography>

    const columns = [
        {
            field: 'id',
            headerName: 'ID',
            sortable: true,
            flex: isMobile ? 0.5 : 0.1,
            minWidth: 50,
        },
        {
            field: 'source',
            headerName: 'Source',
            sortable: true,
            flex: isMobile ? 0.8 : 0.4,
            minWidth: 80,
            renderCell: ({row}) => (
                <Typography sx={{ 
                    fontSize: isMobile ? 12 : 'inherit',
                    whiteSpace: 'normal',
                    lineHeight: 1.2
                }}>
                    {row.source}
                </Typography>
            )
        },
        {
            field: 'detailType',
            headerName: 'Type',
            sortable: true,
            flex: isMobile ? 0.8 : 0.4,
            minWidth: 80,
            renderCell: ({row}) => (
                <Typography sx={{ 
                    fontSize: isMobile ? 12 : 'inherit',
                    whiteSpace: 'normal',
                    lineHeight: 1.2
                }}>
                    {row.detailType}
                </Typography>
            )
        },
        {
            field: 'detail',
            headerName: 'Detail',
            sortable: true,
            flex: 1.5,
            minWidth: 120,
            renderCell: ({row}) => (
                <Box sx={{ width: '100%', overflow: 'hidden' }}>
                    <Typography 
                        sx={{ 
                            fontSize: isMobile ? 12 : 'inherit',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            display: '-webkit-box',
                            WebkitLineClamp: 3,
                            WebkitBoxOrient: 'vertical',
                            whiteSpace: 'normal',
                            lineHeight: 1.2
                        }}
                    >
                        {row.detail}
                    </Typography>
                </Box>
            )
        }
    ];

    return (
        <Card sx={{ 
            maxWidth: '100%',
            overflow: 'hidden',
            padding: 1
        }}>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 1 }}>
                <IconButton 
                    color="error"
                    size="small"
                    onClick={clearHistory}
                >
                    Clear
                    <DeleteIcon />
                </IconButton>
            </Box>
            <Box sx={{ 
                width: '100%', 
                height: { xs: 400, sm: 500, md: 600 },
                '& .MuiDataGrid-root': {
                    '& .MuiDataGrid-cell': {
                        padding: isMobile ? '8px 4px' : '16px',
                    },
                    '& .MuiDataGrid-columnHeader': {
                        padding: isMobile ? '8px 4px' : '16px',
                    },
                    '& .MuiDataGrid-columnHeaderTitle': {
                        fontSize: isMobile ? 12 : 'inherit',
                        fontWeight: 'bold',
                        whiteSpace: 'normal',
                        lineHeight: 1.2
                    }
                }
            }}>
                <DataGrid
                    rows={systemEvents}
                    rowHeight={isMobile ? 60 : 52}
                    columns={columns}
                    pageSizeOptions={isTablet ? [5, 10] : [10, 25]}
                    initialState={{
                        pagination: {
                            paginationModel: {
                                pageSize: isTablet ? 5 : 10,
                            },
                        },
                        sorting: {
                            sortModel: [{field: 'id', sort: 'desc'}]
                        },
                    }}
                    sx={{
                        '& .MuiDataGrid-cell': {
                            whiteSpace: 'normal !important',
                            wordBreak: 'break-word'
                        }
                    }}
                />
            </Box>
        </Card>
    )
}

export default SystemEventsTable;
