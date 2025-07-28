import { Container, Typography } from '@mui/material';

export default function BlogPage() {
  return (
    <Container maxWidth="md" sx={{ py: 8 }}>
      <Typography variant="h4" gutterBottom>Blog</Typography>
      <Typography variant="body1">
        Em breve você encontrará artigos e notícias sobre cidadania e genealogia aqui.
      </Typography>
    </Container>
  );
}
