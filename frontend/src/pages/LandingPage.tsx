import { Box, Button, Container, Typography, Grid, Card, CardContent } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

export default function LandingPage() {
  return (
    <Container maxWidth="md" sx={{ py: 8 }}>
      <Typography variant="h3" gutterBottom>
        A Burocracia Termina Aqui. Encontramos a Certidão Perdida do Seu Antepassado.
      </Typography>
      <Typography variant="h6" color="text.secondary" gutterBottom>
        Cansado de buscas frustradas e de pagar por certidões negativas? Nossa tecnologia de busca automatizada varre os cartórios e arquivos do Brasil para você.
      </Typography>
      <Box sx={{ my: 4 }}>
        <Grid container spacing={4}>
          <Grid item xs={12} md={4}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h5">1. Informe os Dados</Typography>
                <Typography variant="body2">Preencha nosso formulário inteligente com tudo que você sabe.</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h5">2. Nossos Robôs Investigam</Typography>
                <Typography variant="body2">Nossa IA busca em dezenas de fontes online, 24/7.</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h5">3. Receba seu Relatório Completo</Typography>
                <Typography variant="body2">Em poucos dias, acesse seu dashboard e veja a localização da certidão ou um relatório detalhado de todas as buscas realizadas.</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
      <Button
        component={RouterLink}
        to="/novo-pedido"
        variant="contained"
        color="primary"
        size="large"
      >
        Iniciar Minha Busca Agora
      </Button>
    </Container>
  );
}
