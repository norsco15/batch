Step emailStep = new StepBuilder("emailStep", jobRepository)
    .tasklet(emailTasklet(entity), transactionManager)
    .build();


Job job = new JobBuilder("myJob", jobRepository)
    .start(csvOrXlsStep) // chunk step qui écrit sur S3
    .next(emailStep)
    .build();


private Tasklet emailTasklet(SFCMExtractionEntity entity) {
    return (StepContribution contribution, ChunkContext chunkContext) -> {
        // 1) Vérifier si on doit envoyer un mail
        if (!"Y".equalsIgnoreCase(entity.getExtractionMail())) {
            return RepeatStatus.FINISHED;
        }

        // 2) Construire le mail
        MimeMessage message = mailSender.createMimeMessage();
        MimeMessageHelper helper = new MimeMessageHelper(message, true); // multipart = true
        // Récupérer destinataires
        String[] recipients = null;
        if (entity.getExtractionMailEntity() != null) {
            String mailTo = entity.getExtractionMailEntity().getMailTo();
            if (mailTo != null) {
                recipients = mailTo.split(";");
                helper.setTo(recipients);
            }
            helper.setSubject(entity.getExtractionMailEntity().getMailSubject());
            helper.setText(entity.getExtractionMailEntity().getMailBody());
        }

        // 3) Déterminer le nom de fichier S3 + content-type (csv ou xls)
        String extractionType = entity.getExtractionType();
        // ex: on fabrique un objectKey différent
        String objectKey;
        String attachName;
        if ("csv".equalsIgnoreCase(extractionType)) {
            // ex: 
            objectKey = "output/" + entity.getExtractionCSVEntity().getExtractionCSVFileName();
            attachName = entity.getExtractionName() + ".csv";
        } else if ("xls".equalsIgnoreCase(extractionType)) {
            // ex:
            objectKey = "extractions/" + entity.getExtractionName() + ".xlsx";
            attachName = entity.getExtractionName() + ".xlsx";
        } else {
            // type inconnu => on skip
            return RepeatStatus.FINISHED;
        }

        // 4) Télécharger l’objet depuis S3 + attacher
        try {
            S3Object s3Obj = s3Client.getS3().getObject(s3Client.getS3BucketName(), objectKey);
            // Pièce jointe 
            helper.addAttachment(
                attachName, 
                new InputStreamResource(s3Obj.getObjectContent())
            );
        } catch (Exception e) {
            log.warn("Unable to get S3 object => {}", e.getMessage());
        }

        // 5) Envoyer l’email
        mailSender.send(message);

        return RepeatStatus.FINISHED;
    };
}
