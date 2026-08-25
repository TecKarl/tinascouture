from storages.backends.s3 import S3Storage


class SupabaseStorage(S3Storage):
    def url(self, name):
        public_endpoint = self.endpoint_url.replace(
            ".storage.supabase.co/storage/v1/s3",
            ".supabase.co/storage/v1/object/public",
        )

        return (
            f"{public_endpoint}/"
            f"{self.bucket_name}/"
            f"{name}"
        )