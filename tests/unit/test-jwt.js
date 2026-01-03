try {
  const JWT_SECRET = process.env.JWT_SECRET;
  if (!JWT_SECRET) {
    throw new Error('JWT_SECRET environment variable is required for security');
  }
  console.log('JWT_SECRET is set correctly');
} catch (error) {
  console.log('Error:', error.message);
}
