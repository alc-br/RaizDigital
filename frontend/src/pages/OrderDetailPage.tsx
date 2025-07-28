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
} from '@mui/material';
import { fetchOrderDetail } from '../api/api';

interface ResultRecord {
  id: number;
  source_name: string;
  status: string;
  found_data_json?: string;
  screenshot_path?: string;
  timestamp: string;
}

interface OrderDetail {
  id: number;
  status: string;
  target_name: string;
  results: ResultRecord[];
}

export default function OrderDetailPage() {
  const { orderId } = useParams();
  const [order, setOrder] = useState<OrderDetail | null>(null);

  useEffect(() => {
    if (!orderId) return;
    (async () => {
      const data = await fetchOrderDetail(Number(orderId));
      setOrder(data);
    })();
  }, [orderId]);

  if (!order) {
    return (
      <Container maxWidth="md" sx={{ py: 8 }}>
        <Typography>Carregando...</Typography>
      </Container>
    );
  }

  const success = order.status === 'COMPLETED_SUCCESS';

  return (
    <Container maxWidth="md" sx={{ py: 8 }}>
      <Typography variant="h4" gutterBottom>
        Pedido #{order.id}
      </Typography>
      {success ? (
        <Card sx={{ mb: 4, bgcolor: 'success.light' }}>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              Documento Localizado!
            </Typography>
            {/* Display first found result data */}
            {order.results
              .filter((r) => r.status === 'FOUND')
              .map((r) => (
                <Box key={r.id} sx={{ mt: 1 }}>
                  <Typography variant="subtitle1">Fonte: {r.source_name}</Typography>
                  <Typography variant="body2">Dados: {r.found_data_json}</Typography>
                </Box>
              ))}
          </CardContent>
        </Card>
      ) : (
        <Card sx={{ mb: 4, bgcolor: 'info.light' }}>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              Relatório de Busca Exaustiva Concluído
            </Typography>
            <Typography variant="body2">
              Infelizmente não encontramos o documento online. Veja abaixo o relatório completo de buscas.
            </Typography>
          </CardContent>
        </Card>
      )}
      <Typography variant="h5" gutterBottom>
        Resultados
      </Typography>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Fonte Consultada</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Prova</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {order.results.map((result) => (
            <TableRow key={result.id}>
              <TableCell>{result.source_name}</TableCell>
              <TableCell>{result.status}</TableCell>
              <TableCell>{result.screenshot_path ? <a href={result.screenshot_path}>Ver</a> : 'N/A'}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      {!success && (
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
