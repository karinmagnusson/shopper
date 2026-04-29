import NextAuth, { type NextAuthOptions } from 'next-auth'

export const authOptions: NextAuthOptions = {
  providers: [
    {
      id: 'pinterest',
      name: 'Pinterest',
      type: 'oauth',
      authorization: {
        url: 'https://www.pinterest.com/oauth/',
        params: {
          scope: 'boards:read,pins:read,user_accounts:read',
          response_type: 'code',
        },
      },
      token: 'https://api.pinterest.com/v5/oauth/token',
      userinfo: 'https://api.pinterest.com/v5/user_account',
      clientId: process.env.PINTEREST_CLIENT_ID,
      clientSecret: process.env.PINTEREST_CLIENT_SECRET,
      profile(profile: {
        id: string
        username: string
        business_name?: string
        profile_image?: string
        website_url?: string
      }) {
        return {
          id: profile.id,
          name: profile.business_name ?? profile.username,
          email: `${profile.username}@pinterest.placeholder`,
          image: profile.profile_image,
        }
      },
    },
  ],
  callbacks: {
    async jwt({ token, account, profile }) {
      if (account) {
        token.accessToken = account.access_token
        token.refreshToken = account.refresh_token
        token.pinterestId = (profile as { id?: string })?.id
      }
      return token
    },
    async session({ session, token }) {
      session.accessToken = token.accessToken as string | undefined
      session.pinterestId = token.pinterestId as string | undefined
      return session
    },
  },
  pages: {
    signIn: '/',
    error: '/',
  },
  session: {
    strategy: 'jwt',
  },
  secret: process.env.NEXTAUTH_SECRET,
}

export default NextAuth(authOptions)
