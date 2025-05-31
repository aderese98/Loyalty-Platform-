package main

import (
	"log"
	"net/http"
	"os"
	"strconv"

	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

var (
	httpRequestsTotal = prometheus.NewCounterVec(
		prometheus.CounterOpts{
			Name: "http_requests_total",
			Help: "Total number of HTTP requests",
		},
		[]string{"method", "endpoint", "status"},
	)

	httpRequestDuration = prometheus.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "http_request_duration_seconds",
			Help:    "HTTP request duration in seconds",
			Buckets: prometheus.DefBuckets,
		},
		[]string{"method", "endpoint"},
	)
)

func init() {
	prometheus.MustRegister(httpRequestsTotal)
	prometheus.MustRegister(httpRequestDuration)
}

func setupLogger() *zap.Logger {
	config := zap.NewProductionConfig()
	config.EncoderConfig.TimeKey = "timestamp"
	config.EncoderConfig.EncodeTime = zapcore.ISO8601TimeEncoder

	logger, err := config.Build()
	if err != nil {
		log.Fatalf("Failed to create logger: %v", err)
	}
	return logger
}

func initDB() *gorm.DB {
	dsn := "host=postgres user=loyalty password=loyalty123 dbname=loyalty port=5432 sslmode=disable"
	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{
		Logger: logger.Default.LogMode(logger.Info),
	})
	if err != nil {
		log.Fatal("Failed to connect to database:", err)
	}
	return db
}

type UserHandler struct {
	db *gorm.DB
}

func NewUserHandler(db *gorm.DB) *UserHandler {
	return &UserHandler{db: db}
}

func (h *UserHandler) CreateUser(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"message": "User created"})
}

func (h *UserHandler) GetUser(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"message": "User retrieved"})
}

func (h *UserHandler) UpdateUser(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"message": "User updated"})
}

func (h *UserHandler) DeleteUser(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"message": "User deleted"})
}

func main() {
	logger := setupLogger()
	defer logger.Sync()

	// Load environment variables
	if err := godotenv.Load(); err != nil {
		log.Println("No .env file found")
	}

	// Initialize router
	router := gin.New()

	// Add middleware for logging and metrics
	router.Use(gin.Recovery())
	router.Use(func(c *gin.Context) {
		start := prometheus.NewTimer(httpRequestDuration.WithLabelValues(c.Request.Method, c.FullPath()))
		c.Next()
		start.ObserveDuration()

		status := c.Writer.Status()
		httpRequestsTotal.WithLabelValues(c.Request.Method, c.FullPath(), strconv.Itoa(status)).Inc()

		logger.Info("Request processed",
			zap.String("method", c.Request.Method),
			zap.String("path", c.FullPath()),
			zap.Int("status", status),
			zap.Duration("duration", start.ObserveDuration()),
		)
	})

	// Initialize database connection
	db := initDB()

	// Initialize handlers
	userHandler := NewUserHandler(db)

	// Register routes
	api := router.Group("/api/v1")
	{
		users := api.Group("/users")
		{
			users.POST("", userHandler.CreateUser)
			users.GET("/:id", userHandler.GetUser)
			users.PUT("/:id", userHandler.UpdateUser)
			users.DELETE("/:id", userHandler.DeleteUser)
		}
	}

	// Add metrics endpoint
	router.GET("/metrics", gin.WrapH(promhttp.Handler()))

	// Add health check endpoint
	router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "healthy"})
	})

	// Start server
	port := os.Getenv("SERVICE_PORT")
	if port == "" {
		port = "8080"
	}

	logger.Info("Starting server", zap.String("port", port))
	if err := router.Run(":" + port); err != nil {
		logger.Fatal("Failed to start server", zap.Error(err))
	}
} 