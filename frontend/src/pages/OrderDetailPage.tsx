import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Button,
  Chip,
  CircularProgress,
  Alert,
  Link as MuiLink,
  TableContainer,
  Paper,
} from '@mui/material';
import { fetchOrderDetail } from '../api/api';

// Tipagem para os resultados da busca
interface ResultRecord {
  id: number;
  source_name: string;
  status: string;
  details?: string;
  found_data_json?: string;
  screenshot_path?: string;
  timestamp: string;
}

// Tipagem para os detalhes do pedido
interface OrderDetail {
  id: number;
  status: string;
  target_name: string;
  results: ResultRecord[];
}

// Componente para exibir o status com cores
const StatusChip = ({ status }: { status: string }) => {
  let color: 'success' | 'warning' | 'error' | 'info' | 'default' = 'default';
  let label = status;

  switch (status) {
    case 'FOUND':
      color = 'success';
      label = 'Encontrado';
      break;
    case 'NOT_FOUND':
      color = 'warning';
      label = 'Não Encontrado';
      break;
    case 'SOURCE_UNAVAILABLE':
      color = 'error';
      label = 'Fonte Indisponível';
      break;
    case 'ERROR':
      color = 'error';
      label = 'Erro na Busca';
      break;
  }

  return <Chip label={label} color={color} size="small" />;
};


export default function OrderDetailPage() {
  const { orderId } = useParams();
  const [order, setOrder] = useState<OrderDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!orderId) return;
    const getOrder = async () => {
      try {
        setLoading(true);
        const data = await fetchOrderDetail(Number(orderId));
        setOrder(data);
      } catch (error) {
        console.error("Erro ao buscar detalhes do pedido:", error);
      } finally {
        setLoading(false);
      }
    };
    getOrder();
  }, [orderId]);

  if (loading) {
    return (
      <Container maxWidth="md" sx={{ py: 8, textAlign: 'center' }}>
        <CircularProgress />
        <Typography>Carregando detalhes do pedido...</Typography>
      </Container>
    );
  }

  if (!order) {
    return (
      <Container maxWidth="md" sx={{ py: 8 }}>
        <Alert severity="error">Não foi possível carregar os detalhes do pedido.</Alert>
      </Container>
    );
  }

  const isSuccess = order.status === 'COMPLETED_SUCCESS';
  const isProcessing = order.status === 'PROCESSING';

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>
        Detalhes do Pedido #{order.id}
      </Typography>
      <Typography variant="h6" gutterBottom color="text.secondary">
        Busca para: {order.target_name}
      </Typography>

      {/* Card de Resumo do Status */}
      <Card sx={{ mb: 4, bgcolor: isSuccess ? 'success.light' : 'info.light' }}>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            {isSuccess ? 'Documento Localizado!' : 
             isProcessing ? 'Busca em Andamento...' : 'Relatório de Busca Exaustiva Concluído'}
          </Typography>
          <Typography variant="body2">
            {isSuccess ? 'Um ou mais registros foram encontrados. Veja os detalhes na tabela abaixo.' : 
             isProcessing ? 'Nossos robôs estão trabalhando. Os resultados aparecerão aqui assim que forem concluídos.' :
             'Infelizmente não encontramos o documento online. Veja abaixo o relatório completo de cada fonte consultada.'}
          </Typography>
        </CardContent>
      </Card>
      
      {/* Tabela de Resultados Detalhada */}
      <Typography variant="h5" gutterBottom>
        Relatório Detalhado da Busca
      </Typography>
      <TableContainer component={Paper}>
        <Table sx={{ minWidth: 650 }}>
          <TableHead>
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold' }}>Fonte Consultada</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Status</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Detalhes da Busca</TableCell>
              <TableCell sx={{ fontWeight: 'bold' }}>Data</TableCell>
              <TableCell sx={{ fontWeight: 'bold', textAlign:'center' }}>Prova</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {order.results.length > 0 ? (
              order.results.map((result) => (
                <TableRow key={result.id}>
                  <TableCell>{result.source_name}</TableCell>
                  <TableCell>
                    <StatusChip status={result.status} />
                  </TableCell>
                  <TableCell sx={{fontSize: '0.8rem', color: 'text.secondary'}}>{result.details || 'N/A'}</TableCell>
                  <TableCell>{new Date(result.timestamp).toLocaleString()}</TableCell>
                  <TableCell sx={{textAlign:'center'}}>
                    {result.screenshot_path ? (
                      <Button 
                        variant="outlined" 
                        size="small" 
                        component={MuiLink} 
                        href={result.screenshot_path} // Na implementação real, este seria um link válido
                        target="_blank"
                      >
                        Ver Prova
                      </Button>
                    ) : (
                      'N/A'
                    )}
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={5} sx={{ textAlign: 'center' }}>
                  {isProcessing ? 'Aguardando resultados...' : 'Nenhum resultado de busca foi registrado para este pedido.'}
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Seção de Próximos Passos */}
      {!isSuccess && !isProcessing && (
        <Box sx={{ mt: 4, p: 2, border: '1px solid', borderColor: 'grey.300', borderRadius: 1 }}>
          <Typography variant="h6" gutterBottom>
            A busca online não encontrou. E agora?
          </Typography>
          <Typography variant="body2">
            Isso é comum para registros muito antigos. Nossa equipe de especialistas pode iniciar uma busca manual. Conheça nosso serviço de Busca Assistida Premium.
          </Typography>
          <Button variant="contained" color="secondary" sx={{ mt: 2 }}>
            Saber Mais
          </Button>
        </Box>
      )}
    </Container>
  );
}