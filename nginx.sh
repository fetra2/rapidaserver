$params = @{
    Name = "cs_nginx"
    BinaryPathName = "C:\nginx-1.22.1"
    DisplayName = "Nginx"
    StartupType = "Automatic"
    Description = "Location sh file C:\inetpub\wwwroot\rapida"
}
New-Service @params