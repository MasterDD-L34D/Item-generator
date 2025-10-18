import { COOKIE_NAME } from "@shared/const";
import { getSessionCookieOptions } from "./_core/cookies";
import { systemRouter } from "./_core/systemRouter";
import { publicProcedure, router } from "./_core/trpc";
import { getMagicItemsStats } from "./magicItems";
import { generateMagicItem, searchMagicItems, getRandomItems } from "./itemGenerator";
import { z } from "zod";

export const appRouter = router({
  system: systemRouter,

  auth: router({
    me: publicProcedure.query(opts => opts.ctx.user),
    logout: publicProcedure.mutation(({ ctx }) => {
      const cookieOptions = getSessionCookieOptions(ctx.req);
      ctx.res.clearCookie(COOKIE_NAME, { ...cookieOptions, maxAge: -1 });
      return {
        success: true,
      } as const;
    }),
  }),

  // Health check endpoint for testing
  health: router({
    check: publicProcedure.query(() => ({
      status: "ok",
      timestamp: new Date().toISOString(),
      message: "Pathfinder Item Generator API is running"
    })),
  }),

  // Data access test endpoint
  data: router({
    stats: publicProcedure.query(() => {
      try {
        const stats = getMagicItemsStats();
        return {
          success: true,
          ...stats,
        };
      } catch (error) {
        return {
          success: false,
          error: error instanceof Error ? error.message : 'Unknown error',
          totalCount: 0,
          sampleItem: null,
          types: [],
        };
      }
    }),
  }),

  // Magic item generator endpoints
  items: router({
    // Genera un nuovo oggetto magico
    generate: publicProcedure
      .input(z.object({ prompt: z.string().min(1).max(500) }))
      .mutation(async ({ input }) => {
        try {
          const item = await generateMagicItem(input.prompt);
          return { success: true, item };
        } catch (error) {
          return {
            success: false,
            error: error instanceof Error ? error.message : 'Unknown error',
          };
        }
      }),

    // Cerca oggetti magici esistenti
    search: publicProcedure
      .input(z.object({ query: z.string().min(1).max(200), limit: z.number().min(1).max(20).optional() }))
      .query(async ({ input }) => {
        try {
          const items = await searchMagicItems(input.query, input.limit);
          return { success: true, items };
        } catch (error) {
          return {
            success: false,
            error: error instanceof Error ? error.message : 'Unknown error',
            items: [],
          };
        }
      }),

    // Ottieni oggetti casuali per ispirazione
    random: publicProcedure
      .input(z.object({ count: z.number().min(1).max(10).optional() }))
      .query(({ input }) => {
        const items = getRandomItems(input.count || 3);
        return { success: true, items };
      }),
  }),
});

export type AppRouter = typeof appRouter;
